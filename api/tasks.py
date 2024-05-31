import os
import shutil

from celery import shared_task, signals
from django.conf import settings
import numpy as np
import xarray as xr

from nodeorc.models import Task
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
    # replace the subtask output folder
    print(f"Copying video file to {trg}")
    # download file to tmp location
    storage.download_file(task.input_files["videofile"].remote_name, trg, keep_src=True)
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
    """Update video status, file fields and time series after running task. """

    pk, task = args
    video = Video.objects.get(pk=pk)
    task_db = TaskDB.objects.get(id=task["id"])
    video.image = task["output_files"]["jpg"]["remote_name"]
    video.save()
    video = Video.objects.get(pk=pk)
    add_frame_to_model(
        video.image,
        video.thumbnail,
        suffix="_thumb",
        thumb=True
    )
    # read flow information from transect and write to associated time series
    fn = os.path.join(settings.TEMP_FOLDER, task["output_files"]["transect"]["tmp_name"])
    ds = xr.open_dataset(fn)
    Q = np.abs(ds.river_flow.values)
    if "q_nofill" in ds:
        ds.transect.get_river_flow(q_name="q_nofill")
        Q_nofill = np.abs(ds.river_flow.values)
        perc_measured = Q_nofill / Q * 100  # fraction that is truly measured compared to total
    else:
        perc_measured = np.nan * Q
    # fill in time series information
    time_series = video.time_series
    time_series.q_05 = Q[0] if np.isfinite(Q[0]) else None
    time_series.q_25 = Q[1] if np.isfinite(Q[1]) else None
    time_series.q_50 = Q[2] if np.isfinite(Q[2]) else None
    time_series.q_75 = Q[3] if np.isfinite(Q[3]) else None
    time_series.q_95 = Q[4] if np.isfinite(Q[4]) else None
    time_series.fraction_velocimetry = perc_measured[2] if np.isfinite(perc_measured[2]) else None
    time_series.save()

    if state == "SUCCESS":
        video.status = VideoStatus.DONE
        task_db.progress = 1.0
        task_db.status_msg = "Completed successfully"
    else:
        video.status = VideoStatus.ERROR
    video.save()
    task_db.save()
    # remove temporary files
    if not settings.DEBUG:
        shutil.rmtree(settings.TEMP_FOLDER)


@signals.task_failure.connect(sender=run_nodeorc)
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, traceback=None, **kwargs):
    """Update video status and file fields after failing task. """

    pk, task = args
    video = Video.objects.get(pk=pk)
    task_db = TaskDB.objects.get(id=task["id"])
    video.status = VideoStatus.ERROR
    task_db.status_msg = exception
    task_db.progress = 0.0
    video.save()
    task_db.save()
