from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
import json

from api.models import BaseModel, Video, VideoStatus


class TaskStatus(models.IntegerChoices):
    """
    Task status enumeration.
    
    QUEUED: Task has been submitted to compute node but not yet started
    RUNNING: Task is currently being processed on the compute node
    FAILED: Task processing failed on the compute node
    COMPLETED: Task completed on compute node but results not yet synced to server
    CANCELED: Task was explicitly canceled
    DONE: Task completed and results have been synced to server
    """
    QUEUED = 0, "Queued"
    RUNNING = 1, "Running"
    FAILED = 2, "Failed"
    COMPLETED = 3, "Completed"
    CANCELED = 4, "Canceled"
    DONE = 5, "Done"


class Task(BaseModel):
    """
    Task model representing a video processing task executed on a remote compute node.
    
    This model tracks tasks submitted to remote ORC-OS compute nodes. Tasks are 
    decoupled from the server-side processing to allow for distributed computation.
    The task status and progress are synchronized with the compute node via API calls.
    Tasks are temporary things and are deleted after completion or cancellation.
    """
    id = models.AutoField(
        primary_key=True,
        help_text="Local database primary key for the task"
    )
    remote_id = models.IntegerField(
        unique=False,
        null=True,
        blank=True,
        help_text="ID assigned for the video on the compute node. This will be returned when task is submitted."
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        help_text="Video being processed by this task"
    )
    status = models.PositiveSmallIntegerField(
        choices=TaskStatus.choices,
        default=TaskStatus.QUEUED,
        help_text="Current status of the task"
    )
    compute_node = models.ForeignKey(
        'ComputeNode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Compute node running this task"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when task was created"
    )
    uploaded = models.BooleanField(
        default=False,
        help_text="Whether results have been downloaded from the compute node"
    )
    progress = models.FloatField(
        default=0.0,
        help_text="Progress of task execution between 0 and 1"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Task {self.id} (UUID: {self.uuid}) on video {self.video.id}"

    def __repr__(self):
        return f"<Task: id={self.id}, uuid={self.uuid}, status={self.get_status_display()}>"

    def save(self, *args, **kwargs):
        """
        Save the task and update related video status if necessary.
        """
        super(Task, self).save(*args, **kwargs)
        # Update video status when task is created or queued
        video = self.video
        if video.status == VideoStatus.NEW and self.status in [TaskStatus.QUEUED, TaskStatus.RUNNING]:
            video.status = VideoStatus.QUEUE
            video.save()

    @property
    def institute(self):
        """
        Get the institute associated with this task through its video.
        
        Returns
        -------
        Institute
            The institute that owns the site associated with the video
        """
        return self.video.institute

    @property
    def task_body(self):
        """
        Generate the JSON task body to be submitted to the compute node.
        
        This property constructs a JSON payload containing all information needed
        by the compute node to process the video, including video file path,
        processing parameters, and configuration.
        
        Returns
        -------
        dict
            Task configuration dictionary that can be submitted to compute node API
            
        Note
        ----
        Implementation should use video configuration and recipe details to build
        the task body. This is a placeholder for the actual implementation.
        """
        # TODO: Implement task body generation from video and recipe configuration
        # Should include: video path, processing parameters, output format, etc.
        return {
            'video_id': str(self.video.id),
            'task_id': str(self.uuid) if self.uuid else str(self.id),
            # Add more fields based on video configuration and recipe
        }

    def get_status(self):
        """
        Retrieve the current status of the task from the compute node and update local record.
        
        This method makes an API call to the compute node to get the latest task status
        and updates fields like progress, status, and uploaded flag. If the task is
        completed on the node, it marks it as COMPLETED.
        
        Returns
        -------
        bool
            True if status update was successful, False otherwise
            
        Raises
        ------
        Exception
            If compute_node is not set or communication fails
            
        Note
        ----
        This method automatically saves changes to the database.
        """
        if not self.compute_node:
            raise RuntimeError("Cannot get status: task not assigned to a compute node")
        
        try:
            # TODO: Implement API call to compute_node.task_info(self.uuid)
            # Example implementation:
            # task_info = self.compute_node.task_info(self.uuid)
            # self.progress = task_info.get('progress', 0.0)
            # self.status = task_info.get('status', self.status)
            # if task_info.get('completed'):
            #     self.status = TaskStatus.COMPLETED
            # self.uploaded = task_info.get('uploaded', False)
            # self.save()
            # return True
            
            raise NotImplementedError("get_status requires ApiClient implementation")
        except Exception as e:
            print(f"Failed to get status for task {self.id}: {str(e)}")
            raise

    def get_results(self):
        """
        Retrieve information about available results from the compute node.
        
        Returns
        -------
        dict
            Dictionary containing information about available result files and their status
            
        Raises
        ------
        Exception
            If compute_node is not set or communication fails
        """
        if not self.compute_node:
            raise RuntimeError("Cannot get results: task not assigned to a compute node")
        
        try:
            # TODO: Implement API call to compute_node.task_info(self.uuid)
            # Example implementation:
            # return self.compute_node.task_info(self.uuid)
            
            raise NotImplementedError("get_results requires ApiClient implementation")
        except Exception as e:
            print(f"Failed to get results for task {self.id}: {str(e)}")
            raise

    def download_result(self, output_path=None):
        """
        Download results from the compute node once task is completed.
        
        This method should be called after the task reaches COMPLETED or DONE status.
        It retrieves the result files from the compute node and optionally saves them
        to the specified output path.
        
        Parameters
        ----------
        output_path : str, optional
            Local path where results should be saved. If None, results are returned as bytes.
        
        Returns
        -------
        bytes or None
            Result data if output_path is None, None if saved to output_path
            
        Raises
        ------
        RuntimeError
            If task is not completed or not assigned to a compute node
        Exception
            If download fails
        """
        if not self.compute_node:
            raise RuntimeError("Cannot download results: task not assigned to a compute node")
        
        if self.status not in [TaskStatus.COMPLETED, TaskStatus.DONE]:
            raise RuntimeError(f"Cannot download results: task status is {self.get_status_display()}")
        
        try:
            # TODO: Implement result download via compute_node.task_download(self.uuid, output_path)
            # Example implementation:
            # result = self.compute_node.task_download(self.uuid, output_path)
            # if output_path:
            #     self.uploaded = True
            #     self.status = TaskStatus.DONE
            #     self.save()
            # return result
            
            raise NotImplementedError("download_result requires ApiClient implementation")
        except Exception as e:
            print(f"Failed to download results for task {self.id}: {str(e)}")
            raise

    def process(self):
        """
        Submit this task to the best available compute node for processing.
        
        This method finds the compute node with the smallest queue and submits the task.
        If no nodes are available, raises an error. Upon successful submission, updates
        the task with the UUID assigned by the compute node and saves the compute_node
        reference for future status checks.
        
        Returns
        -------
        dict
            Response from the compute node containing task UUID and status information
            
        Raises
        ------
        RuntimeError
            If no compute nodes are available or if a UUID is already assigned
        Exception
            If submission to compute node fails
            
        Note
        ----
        This method automatically saves changes to the database including the assigned
        UUID and compute node reference.
        """
        # Prevent resubmission if task already has a remote_id
        if self.remote_id:
            raise RuntimeError(
                f"Task already submitted to compute node {self.compute_node} with remote ID: {self.remote_id}"
            )
        
        # Import here to avoid circular imports
        from api.models import ComputeNode
        
        # Find the best available compute node
        best_node = ComputeNode.get_best_node()
        if not best_node:
            raise RuntimeError(
                "No compute nodes available for task processing. "
                "Please ensure at least one compute node is online and active."
            )
        
        try:
            # TODO: Implement task submission via best_node.task_process(self)
            # Example implementation:
            # response = best_node.task_process(self)
            # self.remote_id = response.get('id')
            # self.compute_node = best_node
            # self.status = TaskStatus.QUEUED
            # TODO: also save information to self.video on progress / status etc.
            # self.save()
            # return response
            
            raise NotImplementedError("process requires ApiClient implementation")
        except Exception as e:
            print(f"Failed to process task {self.id}: {str(e)}")
            raise

    def delete(self, *args, **kwargs) -> tuple:
        """
        Delete the task from both the compute node and the local database.
        
        This method first attempts to delete the task from the compute node where it
        was submitted, then removes the database record. If the compute node is not set
        (task was never submitted), only the database record is deleted.
        
        Returns
        -------
        tuple
            Tuple of (number of objects deleted, dictionary of deleted objects by model)
            
        Raises
        ------
        Exception
            If deletion from compute node fails
            
        Note
        ----
        This is a hard delete operation that removes the task and its results entirely.
        """
        if self.compute_node and self.remote_id:
            try:
                # TODO: Implement task deletion via compute_node.task_remove(self.remote_id)
                # Example implementation:
                # self.compute_node.task_remove(self.remote_id)
                pass
            except Exception as e:
                print(f"Warning: Failed to delete task from compute node: {str(e)}")
                # Continue with database deletion even if remote deletion fails
        
        # Delete from database
        return super(Task, self).delete(*args, **kwargs)

    def progress_bar(self):
        """
        Generate HTML for a visual progress bar representation.
        
        Returns
        -------
        str
            HTML markup for displaying a progress bar
        """
        percentage = round(self.progress * 100)
        return mark_safe("""
<progress value="{perc}" max="100"></progress>
<span style="font-weight:bold">{perc}%</span>""".format(perc=percentage))

