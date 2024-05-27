import os

from celery import shared_task, signals
from django.conf import settings

from nodeorc.models import Task, Storage
from .models import Video, VideoStatus
from .models import Task as TaskDB
from .models.video import add_frame_to_model


@shared_task(track_started=True)
def run_nodeorc(pk, task_body):
    """
    run nodeorc task through worker.

    Parameters
    ----------
    pk : int
        video primary key
    task_body : dict
        deserialized task in dictionary

    Returns
    -------
    True


    """
    print(f"I received a task with task id: {task_body['id']}")
    task = Task(**task_body)
    storage = task.storage
    trg = os.path.join(settings.TEMP_FOLDER, task.input_files["videofile"].tmp_name)
    output = os.path.join(settings.TEMP_FOLDER, os.path.dirname(task.input_files["videofile"].tmp_name), "OUTPUT")
    # replace the subtask output folder
    print(f"Copying video file to {trg}")
    storage.download_file(task.input_files["videofile"].remote_name, trg, keep_src=True)
    # download file to tmp location
    task.execute(tmp="/tmp/nodeorc", keep_src=True)  #os.path.dirname(trg))
    return True


@signals.task_prerun.connect(sender=run_nodeorc)
def task_prerun_handler(sender, args=None, **kwargs):
    """Update video status to RUNNING upon initialization of task. """

    pk, task_body = args
    video = Video.objects.get(pk=pk)
    video.status = VideoStatus.TASK
    video.save()


@signals.task_postrun.connect(sender=run_nodeorc)
def task_postrun_handler(sender=None, args=None, state=None, retval=None, **kwargs):
    """Update video status and file fields after running task. """

    pk, task = args
    video = Video.objects.get(pk=pk)
    task_db = TaskDB.objects.get(id=task["id"])
    video.image = task["output_files"]["jpg"]["remote_name"]
    add_frame_to_model(video.image, video.thumbnail, suffix="_thumb", thumb=True)
    if state == "SUCCESS":
        video.status = VideoStatus.DONE
        task_db.progress = 1.0
        task_db.traceback = "Completed successfully"
    else:
        video.status = VideoStatus.ERROR
        # TODO: add a traceback
    video.save()
    task_db.save()


@signals.task_failure.connect(sender=run_nodeorc)
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, traceback=None, **kwargs):
    """Update video status and file fields after running task. """

    pk, task = args
    video = Video.objects.get(pk=pk)
    task_db = TaskDB.objects.get(id=task["id"])
    video.status = VideoStatus.ERROR
    task_db.traceback = exception
    task_db.progress = 0.0
    # TODO: add a traceback
    video.save()
    task_db.save()
