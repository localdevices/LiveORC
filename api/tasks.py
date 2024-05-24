import os

from celery import shared_task, signals
from django.conf import settings

from nodeorc.models import Task, Storage
# from .models import Video, VideoStatus
import time



@shared_task(track_started=True)
def run_nodeorc(pk, task_body):
    print(f"I received a task with task id: {task_body['id']}")
    task = Task(**task_body)
    storage = task.storage
    trg = os.path.join(settings.TEMP_FOLDER, task.input_files["videofile"].tmp_name)
    output = os.path.join(settings.TEMP_FOLDER, os.path.dirname(task.input_files["videofile"].tmp_name), "OUTPUT")
    # replace the subtask output folder
    print(f"Copying video file to {trg}")
    # storage.download_file(task.input_files["videofile"].remote_name, trg, keep_src=True)
    # download file to tmp location
    task.execute(tmp="/tmp/nodeorc", keep_src=True)  #os.path.dirname(trg))
    time.sleep(10)
    print("PLEASE CHECK IF I HAVE BEEN RUNNING")
    return True
#
#
# @signals.task_prerun.connect(sender=run_nodeorc)
# def task_prerun_handler(sender, args=None, **kwargs):
#     print("RECEIVED TASK {task_body['id'], UPDATE VIDEO STATUS")
#     pk, task_body = args
#     print(f"VIDEO ID: {pk}")
#     video = Video.objects.get(pk=pk)
#     video.status = VideoStatus.TASK
#     video.save()
#
#
# @signals.task_postrun.connect(sender=run_nodeorc)
# def task_postrun_handler(sender=None, args=None, state=None, retval=None, **kwargs): #task_id=None, task=None, args=None, kwargs=None, retval=None, state=None):
#     print(retval)
#     print(state)
#     pk = args[0]
#     video = Video.objects.get(pk=pk)
#     if state == "SUCCESS":
#     # pk = kwargs['args'][0]  # assuming the first argument is some_parameter
#         video.status = VideoStatus.DONE
#     else:
#         video.status = VideoStatus.ERROR
#     video.save()
#
#
