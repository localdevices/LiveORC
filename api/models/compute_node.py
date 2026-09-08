from django.contrib.gis.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid
from datetime import timedelta

from api.models import BaseModelNoInstitute


class ComputeNode(BaseModelNoInstitute):
    """
    Compute Node model representing a remote ORC-OS instance that can process tasks.
    
    A compute node is a remote server running ORC-OS that can execute video processing
    tasks. This model stores connection information, status, and queue management.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Unique identifier of compute node"
    )
    hostname = models.CharField(
        max_length=255,
        help_text="Hostname or IP address of the compute node"
    )
    port = models.PositiveIntegerField(
        help_text="API port number of the compute node"
    )
    label = models.CharField(
        max_length=255,
        help_text="Recognizable label or name for this compute node"
    )
    api_version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="API version of the compute node"
    )
    token = models.CharField(
        max_length=500,
        help_text="Authentication token/password for secure communication with the node"
    )
    queue_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of tasks currently queued on this compute node"
    )
    last_refreshed = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp of the last successful status update from the node"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text="Timestamp when this compute node was registered"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this node is actively used for task distribution"
    )

    class Meta:
        verbose_name = "Compute Node"
        verbose_name_plural = "Compute Nodes"
        ordering = ['-last_refreshed']

    def __str__(self):
        return f"{self.label} ({self.hostname}:{self.port})"

    def __repr__(self):
        return f"<ComputeNode: {self.label}>"

    @property
    def is_online(self):
        """
        Check if the compute node is currently online.
        
        A node is considered online if it has been refreshed within the last 5 minutes
        and is marked as active.
        
        Returns
        -------
        bool
            True if the node is online, False otherwise
        """
        if not self.is_active:
            return False
        
        time_threshold = timezone.now() - timedelta(minutes=5)
        return self.last_refreshed >= time_threshold

    @property
    def client(self):
        """
        Get an API client for communicating with this compute node.
        
        Returns
        -------
        ApiClient
            A client instance configured for this node's hostname, port, and token
            
        Note
        ----
        ApiClient to be implemented in api/clients.py or similar module
        """
        # Placeholder: Import and return ApiClient when implemented
        # from api.clients import ApiClient
        # return ApiClient(
        #     hostname=self.hostname,
        #     port=self.port,
        #     token=self.token,
        #     api_version=self.api_version
        # )
        raise NotImplementedError("ApiClient not yet implemented")

    def update(self):
        """
        Fetch the latest status information from the compute node and update the database entry.
        
        This method makes a request to the node's status endpoint to retrieve current
        queue count, API version, and other status information, then updates the local record.
        
        Returns
        -------
        bool
            True if update was successful, False otherwise
            
        Raises
        ------
        Exception
            If communication with the node fails
        """
        try:
            # TODO: Implement actual API call to node status endpoint
            # Example implementation:
            # response = self.client.get_status()
            # self.queue_count = response.get('queue_count', 0)
            # self.api_version = response.get('api_version', self.api_version)
            # self.last_refreshed = timezone.now()
            # self.save()
            # return True
            
            raise NotImplementedError("Update method requires ApiClient implementation")
        except Exception as e:
            # Log the error but don't raise to allow graceful degradation
            print(f"Failed to update ComputeNode {self.label}: {str(e)}")
            return False

    def task_process(self, task):
        """
        Submit a task to this compute node for processing.
        
        Parameters
        ----------
        task : Task or str or UUID
            Either a Task instance or a task UUID. If UUID is provided, the Task 
            instance will be retrieved from the database
        
        Returns
        -------
        dict
            Response from the node containing task status/ID or error information
            
        Raises
        ------
        ValueError
            If task parameter is invalid
        Exception
            If communication with the node fails
        """
        from uuid import UUID
        # TODO: Import Task model when ready
        # from api.models import Task
        
        # Handle both Task instance and UUID
        if isinstance(task, (str, UUID)):
            # TODO: Retrieve Task instance from database
            # task_uuid = UUID(task) if isinstance(task, str) else task
            # task = Task.objects.get(id=task_uuid)
            pass
        elif task is None:
            raise ValueError("Task cannot be None")
        
        try:
            # TODO: Implement actual API call to submit task
            # Example implementation:
            # payload = {
            #     'task_id': str(task.id),
            #     'task_body': task.task_body,
            # }
            # response = self.client.create_task(payload)
            # return response
            
            raise NotImplementedError("task_process requires ApiClient implementation")
        except Exception as e:
            print(f"Failed to process task on ComputeNode {self.label}: {str(e)}")
            raise

    def task_info(self, task_id=None):
        """
        Retrieve current information on tasks from this compute node.
        
        Parameters
        ----------
        task_id : str or UUID, optional
            If provided, retrieve info for a specific task. If None, retrieve info 
            for all tasks on this node.
        
        Returns
        -------
        dict
            Task information from the node (specific task or list of tasks)
            
        Raises
        ------
        Exception
            If communication with the node fails
        """
        try:
            # TODO: Implement actual API call to retrieve task info
            # Example implementation:
            # if task_id:
            #     return self.client.get_task(str(task_id))
            # else:
            #     return self.client.list_tasks()
            
            raise NotImplementedError("task_info requires ApiClient implementation")
        except Exception as e:
            print(f"Failed to retrieve task info from ComputeNode {self.label}: {str(e)}")
            raise

    def task_cancel(self, task_id):
        """
        Cancel a task that is running or queued on this compute node.
        
        Parameters
        ----------
        task_id : str or UUID
            The ID of the task to cancel
        
        Returns
        -------
        dict
            Response from the node indicating success or failure
            
        Raises
        ------
        Exception
            If communication with the node fails
        """
        try:
            # TODO: Implement actual API call to cancel task
            # Example implementation:
            # return self.client.cancel_task(str(task_id))
            
            raise NotImplementedError("task_cancel requires ApiClient implementation")
        except Exception as e:
            print(f"Failed to cancel task on ComputeNode {self.label}: {str(e)}")
            raise

    def task_remove(self, task_id):
        """
        Remove a task from this compute node (removes from queue or storage).
        
        Parameters
        ----------
        task_id : str or UUID
            The ID of the task to remove
        
        Returns
        -------
        dict
            Response from the node indicating success or failure
            
        Raises
        ------
        Exception
            If communication with the node fails
        """
        try:
            # TODO: Implement actual API call to remove task
            # Example implementation:
            # return self.client.remove_task(str(task_id))
            
            raise NotImplementedError("task_remove requires ApiClient implementation")
        except Exception as e:
            print(f"Failed to remove task on ComputeNode {self.label}: {str(e)}")
            raise

    def task_download(self, task_id, output_path=None):
        """
        Download results of a completed task from this compute node.
        
        Parameters
        ----------
        task_id : str or UUID
            The ID of the task to download results for
        output_path : str, optional
            Local path where results should be saved. If None, returns raw data/stream
        
        Returns
        -------
        bytes or None
            Task results data if output_path is None, None if saved to output_path
            
        Raises
        ------
        Exception
            If communication with the node fails or download fails
        """
        try:
            # TODO: Implement actual API call to download task results
            # Example implementation:
            # if output_path:
            #     return self.client.download_task(str(task_id), output_path)
            # else:
            #     return self.client.get_task_results(str(task_id))
            
            raise NotImplementedError("task_download requires ApiClient implementation")
        except Exception as e:
            print(f"Failed to download task results from ComputeNode {self.label}: {str(e)}")
            raise

    def task_restart(self, task_id):
        """
        Restart a task on this compute node.
        
        This can be useful if a task failed or needs to be re-processed.
        
        Parameters
        ----------
        task_id : str or UUID
            The ID of the task to restart
        
        Returns
        -------
        dict
            Response from the node indicating success or failure
            
        Raises
        ------
        Exception
            If communication with the node fails
        """
        try:
            # TODO: Implement actual API call to restart task
            # Example implementation:
            # return self.client.restart_task(str(task_id))
            
            raise NotImplementedError("task_restart requires ApiClient implementation")
        except Exception as e:
            print(f"Failed to restart task on ComputeNode {self.label}: {str(e)}")
            raise

    @staticmethod
    def get_best_node():
        """
        Find the best available compute node for the next job.
        
        Selection criteria (in order of priority):
        1. Node must be active and online (last_refreshed within 5 minutes)
        2. Node with the lowest queue_count (fewest pending tasks)
        
        Returns
        -------
        ComputeNode or None
            The best available node, or None if no nodes are online
            
        Examples
        --------
        >>> best_node = ComputeNode.get_best_node()
        >>> if best_node:
        ...     best_node.task_process(task)
        """
        # Get all active nodes that are online (refreshed within last 5 minutes)
        time_threshold = timezone.now() - timedelta(minutes=5)
        
        available_nodes = ComputeNode.objects.filter(
            is_active=True,
            last_refreshed__gte=time_threshold
        ).order_by('queue_count')
        
        if available_nodes.exists():
            return available_nodes.first()
        
        return None
