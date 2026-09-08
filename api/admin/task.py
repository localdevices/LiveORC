from django import forms
from django.contrib import messages
from django.contrib.gis import admin

from api.admin import BaseAdmin, BaseForm, TaskInstituteFilter
from api.models import Task, TaskStatus, Video


class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks.
    
    Users can only select videos they have access to.
    Most fields are automatically managed and read-only.
    """
    
    class Meta:
        model = Task
        fields = ['video']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        
        # Set all available videos initially
        queryset = Video.objects.all()
        
        # Filter videos based on user permissions
        if self.request and not self.request.user.is_superuser:
            memberships = self.request.user.get_memberships()
            institutes = [m.institute for m in memberships]
            # Filter to videos from institutes the user has access to
            queryset = queryset.filter(
                video_config__camera_config__site__institute__in=institutes
            )
        
        # Update the video field queryset
        video_field = self.fields.get('video')
        if video_field and isinstance(video_field, forms.ModelChoiceField):
            video_field.queryset = queryset
        
        self.fields['video'].help_text = "Select the video to process"


class TaskAdmin(BaseAdmin):
    """
    Admin interface for Task model.
    
    Tasks can be created by users only if they have write access to the video.
    Tasks can only be deleted if the user has change/delete permissions on the associated video.
    
    Most fields are read-only since the actual task processing is managed by compute nodes.
    """
    
    form = TaskForm
    readonly_fields = [
        'id',
        'remote_id',
        'status',
        'compute_node',
        'created_at',
        'uploaded',
        'progress',
        'get_task_status_display'
    ]
    
    list_display = [
        'id',
        'get_video_label',
        'get_status_badge',
        'progress',
        'compute_node',
        'created_at'
    ]
    
    list_filter = [TaskInstituteFilter, 'status', 'created_at']
    search_fields = ['id', 'remote_id', 'video__id']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('id', 'remote_id', 'video'),
            'description': 'Basic task information'
        }),
        ('Status & Processing', {
            'fields': ('status', 'get_task_status_display', 'progress', 'uploaded', 'compute_node'),
            'description': 'Current status and processing information from the compute node'
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'description': 'System-generated metadata',
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Create New Task', {
            'fields': ('video',),
            'description': 'Select a video to create a processing task for it'
        }),
    )

    def has_add_permission(self, request):
        """
        Allow users to create tasks if they have at least one institute membership.
        This does not yet filter by video permissions, which is handled in the form.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        
        Returns
        -------
        bool
            True if user is superuser or has institute memberships
        """
        if request.user.is_superuser:
            return True
        return len(request.user.get_owned_institute_memberships()) > 0

    def has_change_permission(self, request, obj=None):
        """
        Users cannot change tasks after creation (only view).
        Only superusers can modify tasks.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : Task, optional
            The task object
        
        Returns
        -------
        bool
            True only if user is superuser
        """
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """
        Users can delete a task only if they have delete permission on the associated video.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : Task, optional
            The task object
        
        Returns
        -------
        bool
            True if user can delete the task's video or is superuser
        """
        if request.user.is_superuser:
            return True
        
        if obj:
            # Check if user has change/delete permission on the video
            from django.contrib.admin import site as admin_site
            video_model_admin = admin_site._registry.get(Video)
            if video_model_admin:
                return video_model_admin.has_delete_permission(request, obj.video) or \
                       video_model_admin.has_change_permission(request, obj.video)
        
        return False

    def has_view_permission(self, request, obj=None):  # type: ignore[override]
        """
        Users can view tasks if they have access to the associated video.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : Task, optional
            The task object
        
        Returns
        -------
        bool or None
            True if user is superuser or has institute membership
        """
        if request.user.is_superuser:
            return True
        if obj is None:
            # List view - show if user has any memberships
            return len(request.user.get_membership_institutes()) > 0
        if obj.institute in request.user.get_membership_institutes():
            return True
        return None

    def get_queryset(self, request):
        """
        Filter queryset based on user permissions.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        
        Returns
        -------
        QuerySet
            Filtered queryset
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(video__video_config__camera_config__site__institute__in=institutes)

    def get_fieldsets(self, request, obj=None):  # type: ignore[override]
        """
        Return fieldsets based on whether we're creating or editing.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : Task, optional
            The task object (None if creating new)
        
        Returns
        -------
        list
            List of fieldsets
        """
        if obj is None:
            return list(self.add_fieldsets)
        else:
            fieldsets = self.fieldsets
            return list(fieldsets) if fieldsets else []

    def get_readonly_fields(self, request, obj=None):
        """
        Make all fields except 'video' read-only when creating.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        obj : Task, optional
            The task object (None if creating new)
        
        Returns
        -------
        list
            List of read-only field names
        """
        readonly = list(self.readonly_fields)
        if obj is not None:
            # When editing, everything is read-only
            readonly.append('video')
        return readonly

    def get_task_status_display(self, obj):
        """
        Display the task status in a human-readable format.
        
        Parameters
        ----------
        obj : Task
            The task object
        
        Returns
        -------
        str
            Human-readable status
        """
        if obj.status == TaskStatus.QUEUED:
            return '⏳ Queued'
        elif obj.status == TaskStatus.RUNNING:
            return '▶️ Running'
        elif obj.status == TaskStatus.FAILED:
            return '❌ Failed'
        elif obj.status == TaskStatus.COMPLETED:
            return '✅ Completed (Not Synced)'
        elif obj.status == TaskStatus.CANCELED:
            return '⛔ Canceled'
        elif obj.status == TaskStatus.DONE:
            return '✅ Done'
        else:
            return obj.get_status_display()
    
    # Set attributes for display
    setattr(get_task_status_display, 'short_description', 'Status Display')

    def get_status_badge(self, obj):
        """
        Display the task status as a colored badge.
        
        Parameters
        ----------
        obj : Task
            The task object
        
        Returns
        -------
        str
            HTML markup for a status badge
        """
        status_colors = {
            TaskStatus.QUEUED: '#FFA500',      # Orange
            TaskStatus.RUNNING: '#4169E1',     # Blue
            TaskStatus.FAILED: '#DC143C',      # Crimson
            TaskStatus.COMPLETED: '#FFD700',   # Gold
            TaskStatus.CANCELED: '#808080',    # Gray
            TaskStatus.DONE: '#228B22',        # Forest Green
        }
        
        color = status_colors.get(obj.status, '#000000')
        status_text = obj.get_status_display()
        
        return f'<span style="background-color: {color}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{status_text}</span>'
    
    # Set attributes for display
    setattr(get_status_badge, 'allow_tags', True)
    setattr(get_status_badge, 'short_description', 'Status')

    def get_video_label(self, obj):
        """
        Display the associated video label.
        
        Parameters
        ----------
        obj : Task
            The task object
        
        Returns
        -------
        str
            Video identifier or label
        """
        return str(obj.video.id)
    
    # Set attributes for display
    setattr(get_video_label, 'short_description', 'Video')

    def filter_institute(self, request, qs):
        """
        Filter queryset by institutes the user has membership in.
        
        Parameters
        ----------
        request : HttpRequest
            The HTTP request object
        qs : QuerySet
            The queryset to filter
        
        Returns
        -------
        QuerySet
            Filtered queryset
        """
        if request.user.is_superuser:
            return qs
        
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(video__video_config__camera_config__site__institute__in=institutes)
