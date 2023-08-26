# helper functions to develop tasks from models
from nodeorc import models


def get_task(instance):
    """
    Make a full task dict from the current video

    Parameters
    ----------
    instance

    Returns
    -------

    """
    # prepare callback

def get_recipe(instance):
    """
    Serializes recipe to dict form, acceptable by nodeorc

    Parameters
    ----------
    instance : recipe model instance

    Returns
    -------
    nodeorc.models...

    """

def get_storage(storage):
    """
    translates storage parameters into nodeodm Storage object

    Parameters
    ----------
    storage

    Returns
    -------

    """
    return models.Storage(**kwargs)

def get_subtasks(instance, task_type="all"):
    """
    Translates video object into a full list of subtasks. The list of subtasks can be defined or automatically
    derived form the structure of the video.

    Parameters
    ----------
    instance

    Returns
    -------
    list
        set of nodeorc.models.Subtask types
    """
    # subtasks = [
    #     {
    #         "name": "velocity_flow",
    #         "kwargs":,
    #     "callback":,
    # "input_files": {"videofile":}
    # }
    # ]

    return [models.Subtask(**kwargs)]


def callback_url():
    """
    Dynamically generates the main end point with token where any sub callback should go to

    Returns
    -------

    """
def callback():
    return models.Callback(
        func_name="post_discharge",
        kwargs={},
        callback_endpoint="/processing/examplevideo/discharge"  # used to extend the default callback url
    )


def input_file():
    """
    Converts a storage + file location into a File object for nodeorc

    Returns
    -------

    """
    return models.File(
        remote_name="piv.nc",
        tmp_name="OUTPUT/piv.nc",
    )

def kwargs_velocimetry():
    """
    Collects video file, camera config, recipe and output location into one set of kwargs for velocimetry processor

    Returns
    -------

    """
    kwargs = {
        "videofile": "video.mp4",
        "cameraconfig": camconfig,
        "recipe": recipe,
        "output": os.path.join(temp_path, "OUTPUT"),
        "prefix": ""
    }
    return kwargs