from django import forms
from django.contrib import messages
from django.contrib.gis import admin
from django.utils import timezone

from api.models import ComputeNode


class ComputeNodeForm(forms.ModelForm):
    """
    Form for creating and editing compute nodes.
    
    Only allows input of hostname, port, label, and token fields.
    Other fields are populated automatically.
    """
    
    class Meta:
        model = ComputeNode
        fields = ['hostname', 'port', 'label', 'token']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ComputeNodeForm, self).__init__(*args, **kwargs)
        
        # Set field help texts
        self.fields['hostname'].help_text = "Hostname or IP address of the compute node"
        self.fields['port'].help_text = "API port number (default: 8000)"
        self.fields['label'].help_text = "Recognizable name for this compute node"
        self.fields['token'].help_text = "Authentication token/password for the compute node"
        
        # Make token field password-style
        self.fields['token'].widget = forms.PasswordInput(render_value=False)


class ComputeNodeChangeForm(forms.ModelForm):
    """
    Form for editing an existing compute node.
    
    Allows modification of hostname, port, label, and authentication token.
    All fields are optional to allow partial updates.
    """
    
    new_token = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        required=False,
        label="New Token",
        help_text="Leave empty if you do not want to change the token"
    )
    
    class Meta:
        model = ComputeNode
        fields = ['hostname', 'port', 'label']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make all model fields optional for partial updates
        for field_name in self.fields:
            self.fields[field_name].required = False
        
        # Set help texts
        self.fields['hostname'].help_text = "Leave empty to keep current hostname"
        self.fields['port'].help_text = "Leave empty to keep current port"
        self.fields['label'].help_text = "Leave empty to keep current label"

    def save(self, commit=True):
        """
        Save the updated fields to the model.
        
        Only updates fields that have been provided (non-empty values).
        
        Parameters
        ----------
        commit : bool
            Whether to save to database immediately
            
        Returns
        -------
        ComputeNode
            The saved model instance
        """
        # Call parent save with commit=False to set up save_m2m
        instance = super().save(commit=False)
        
        # Only update hostname if provided
        if self.cleaned_data.get('hostname'):
            instance.hostname = self.cleaned_data['hostname']
        
        # Only update port if provided
        if self.cleaned_data.get('port'):
            instance.port = self.cleaned_data['port']
        
        # Only update label if provided
        if self.cleaned_data.get('label'):
            instance.label = self.cleaned_data['label']
        
        # Only update token if provided
        if self.cleaned_data.get('new_token'):
            instance.token = self.cleaned_data['new_token']
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


class ComputeNodeAdmin(admin.GISModelAdmin):
    """
    Admin interface for ComputeNode model.
    
    Only superusers can create new compute nodes. When a new node is created,
    the system attempts to connect to it to verify availability and retrieve
    the API version. If the connection fails, a warning is displayed but the
    node is still added to the database with is_active=False.
    
    The token field is hidden when viewing existing nodes for security.
    Superusers can change the token through a separate fieldset if it has been modified.
    """
    
    form = ComputeNodeForm
    readonly_fields = ['id', 'created_at', 'last_refreshed', 'queue_count', 'api_version', 'is_active']
    
    list_display = [
        'label',
        'hostname',
        'port',
        'is_online_status',
        'queue_count',
        'last_refreshed',
        'is_active'
    ]
    
    list_filter = ['is_active', 'created_at']
    search_fields = ['label', 'hostname']
    
    # Fieldsets for creating new nodes
    add_fieldsets = (
        ('Connection Information', {
            'fields': ('hostname', 'port', 'label', 'token'),
            'description': 'Configure the compute node connection parameters.'
        }),
    )
    
    # Fieldsets for editing existing nodes (token hidden for security)
    change_fieldsets = (
        ('Connection Information', {
            'fields': ('label', 'hostname', 'port'),
            'description': 'Configure the compute node connection parameters.'
        }),
        ('Change Authentication Token', {
            'fields': ('new_token',),
            'description': 'Leave empty if you do not want to change the token.',
            'classes': ('collapse',)
        }),
        # ('Status Information', {
        #     'fields': ('is_active', 'api_version', 'queue_count', 'last_refreshed'),
        #     'description': 'Automatically updated status information from the node.',
        #     'classes': ('collapse',)
        # }),
        # ('Metadata', {
        #     'fields': ('id', 'created_at'),
        #     'description': 'System-generated metadata.',
        #     'classes': ('collapse',)
        # }),
    )

    def has_add_permission(self, request):
        """
        Only superusers can add new compute nodes.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        
        Returns
        -------
        bool
            True if user is a superuser, False otherwise
        """
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """
        Only superusers can delete compute nodes.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : ComputeNode, optional
            The object being deleted (if any)
        
        Returns
        -------
        bool
            True if user is a superuser, False otherwise
        """
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """
        Only superusers can modify compute nodes.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : ComputeNode, optional
            The object being modified (if any)
        
        Returns
        -------
        bool
            True if user is a superuser, False otherwise
        """
        return request.user.is_superuser

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Return the appropriate form based on whether we're creating or editing.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : ComputeNode, optional
            The compute node object (None if creating new)
        change : bool
            Whether this is a change (edit) operation
        **kwargs
            Additional keyword arguments
        
        Returns
        -------
        Form
            The appropriate form class for create or edit
        """
        if obj is None:
            # Creating new node - use ComputeNodeForm with token field
            return ComputeNodeForm
        else:
            # Editing existing node - use ComputeNodeChangeForm (allows hostname, port, label updates)
            return ComputeNodeChangeForm

    def get_fieldsets(self, request, obj=None):  # type: ignore[override]
        """
        Return fieldsets based on whether we're creating or editing.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : ComputeNode, optional
            The compute node object (None if creating new)
        
        Returns
        -------
        list
            List of fieldsets appropriate for create or edit
        """
        if obj is None:
            return list(self.add_fieldsets)
        else:
            return list(self.change_fieldsets)

    def get_readonly_fields(self, request, obj=None):
        """
        Make certain fields read-only based on whether we're creating or editing.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : ComputeNode, optional
            The compute node object (None if creating new)
        
        Returns
        -------
        list
            List of field names that should be read-only
        """
        if obj:
            # When editing, make ID read-only
            return list(self.readonly_fields) + ['id']
        else:
            # When creating, only show connection fields as editable
            return []

    def is_online_status(self, obj):
        """
        Display whether a compute node is currently online.
        
        Parameters
        ----------
        obj : ComputeNode
            The compute node object
        
        Returns
        -------
        bool
            True if node is online, False otherwise
        """
        return obj.is_online
    
    # Set attributes for Django admin display
    setattr(is_online_status, 'boolean', True)
    setattr(is_online_status, 'short_description', 'Online')

    def save_model(self, request, obj, form, change):
        """
        Save the compute node model after attempting to connect to the node.
        
        When creating a new node (not editing), attempts to make an API call to
        retrieve the node's status and API version. If successful, sets is_active=True.
        If the connection fails, displays a warning message and sets is_active=False
        with empty api_version, but still saves the node to the database.
        
        When editing an existing node, handles updates to hostname, port, label, and token.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : ComputeNode
            The compute node object being saved
        form : Form
            The form used for editing (ComputeNodeForm for creation, ComputeNodeChangeForm for edit)
        change : bool
            True if this is an existing object being modified, False if creating new
        """
        # Set the creator field for new objects
        if not change:
            obj.creator = request.user
            # This is a new compute node, try to connect and verify
            self._verify_and_configure_node(obj, request)
        else:
            # Editing existing node - track what changed for messaging
            token_changed = bool(form.cleaned_data.get('new_token'))
            super().save_model(request, obj, form, change)
            
            if token_changed:
                messages.success(request, f"Token updated for compute node '{obj.label}'.")
            messages.info(request, f"Compute node '{obj.label}' updated successfully.")
            return
        
        super().save_model(request, obj, form, change)

    def _verify_and_configure_node(self, obj, request):
        """
        Attempt to verify and configure a compute node by connecting to it.
        
        Makes an API call to the node to check if it's online and retrieve its
        API version. Sets appropriate status flags and displays messages to the user.
        
        Parameters
        ----------
        obj : ComputeNode
            The compute node object to verify
        request : HttpRequest
            The HTTP request object (for displaying messages)
        """
        try:
            # TODO: Implement actual API call to node status endpoint
            # Example implementation:
            # response = obj.update()
            # if response:
            #     obj.is_active = True
            #     messages.success(
            #         request,
            #         f"Successfully connected to compute node '{obj.label}'. "
            #         f"API version: {obj.api_version}"
            #     )
            # else:
            #     raise RuntimeError("Failed to retrieve node status")
            
            # Placeholder: Assume connection succeeded for now
            obj.is_active = True
            obj.last_refreshed = timezone.now()
            messages.success(
                request,
                f"Compute node '{obj.label}' added successfully. "
                f"(Note: Actual connection verification not yet implemented)"
            )
            
        except Exception as e:
            # Connection failed, but still add to database
            obj.is_active = False
            obj.api_version = ""
            obj.last_refreshed = timezone.now()
            
            messages.warning(
                request,
                f"⚠️  Warning: Could not connect to compute node '{obj.label}' at "
                f"{obj.hostname}:{obj.port}. The node may be offline or unreachable. "
                f"The node has been added to the database with is_active=False. "
                f"Error: {str(e)}"
            )
