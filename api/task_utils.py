import os

from django.conf import settings
from django.urls import reverse
# helper functions to develop tasks from models
from nodeorc import models
from api.models import Video, CameraConfig
from api import callback_utils

OUTPUT_FILES_ALL = {
    "piv": {
        "remote_name": "piv.nc",
        "tmp_name": "OUTPUT/piv.nc"
    },
    "transect": {
        "remote_name": "transect_1.nc",
        "tmp_name": "OUTPUT/transect_transect_1.nc"
    },
    "piv_mask": {
        "remote_name": "piv_mask.nc",
        "tmp_name": "OUTPUT/piv_mask.nc"
    },
    "jpg": {
        "remote_name": "plot_quiver.jpg",
        "tmp_name": "OUTPUT/plot_quiver.jpg"
    }

}

# this is used when a task_form is created
OUTPUT_FILES_ALL_TEMPLATE = {
    "piv": {
        "remote_name": "piv_{}.nc",
        "tmp_name": "OUTPUT/piv.nc"
    },
    "transect": {
        "remote_name": "transect_1_{}.nc",
        "tmp_name": "OUTPUT/transect_transect_1.nc"
    },
    "piv_mask": {
        "remote_name": "piv_mask_{}.nc",
        "tmp_name": "OUTPUT/piv_mask.nc"
    },
    "jpg": {
        "remote_name": "plot_quiver_{}.jpg",
        "tmp_name": "OUTPUT/plot_quiver.jpg"
    }

}


def get_task_form(
    instance,
    query_callbacks,
    serialize=False,
):
    """
    Retrieve a subtask form for repetitive use on nodeORC, e.g. for a fixed site

    Parameters
    ----------
    instance : CameraConfig
        Camera configuration for which to create a Task Form
    query_callbacks : list[str]
        names of callbacks to retrieve for the instance
    request : request
    serialize : bool
        Defines whether to serialize the task or leave it as a nodeorc Task Object
    *args : list
        additional args to parse
    **kwargs : dict
        additional kwargs to parse

    Returns
    -------
    dict (serialized) or nodeorc.models.Task (not serialized)
    """
    subtasks = get_subtasks_form(instance)
    output_files = OUTPUT_FILES_ALL_TEMPLATE
    callbacks = get_callbacks(instance, query_callbacks)
    task_form = models.Task(
        subtasks=subtasks,
        output_files=output_files,
        callbacks=callbacks,
    )
    return task_form.to_json(serialize=serialize)


def get_task(
        instance,
        request,
        query_callbacks=(
            "get_form_callback_video_no_file_post",
            "get_form_callback_discharge_post",
        ),
        serialize=True,
        *args,
        **kwargs
):
    """
    Make a full task dict from the current video

    Parameters
    ----------
    instance : Video
        Video object for which to create a single task
    request : request
    query_callbacks : list[str]
        callback functions to apply after the task is computed
    serialize : bool
        Defines whether to serialize the task or leave it as a nodeorc Task Object
    *args : list
        additional args to parse
    **kwargs : dict
        additional kwargs to parse

    Returns
    -------
    dict (serialized) or nodeorc.models.Task (not serialized)

    """
    storage = get_storage(instance)
    subpath = os.path.dirname(str(instance.file))
    datetimestr = os.path.splitext(os.path.basename(str(instance.file)))[0]
    output_files = {
        "piv": {
            "remote_name": os.path.join(subpath, f"piv_{datetimestr}.nc"),
            "tmp_name": os.path.join(subpath, "OUTPUT/piv.nc"),
        },
        "transect": {
            "remote_name": os.path.join(subpath, f"transect_1_{datetimestr}.nc"),
            "tmp_name": os.path.join(subpath, "OUTPUT/transect_transect_1.nc"),
        },
        "piv_mask": {
            "remote_name": os.path.join(subpath, f"piv_mask_{datetimestr}.nc"),
            "tmp_name": os.path.join(subpath, "OUTPUT/piv_mask.nc"),
        },
        "jpg": {
            "remote_name": os.path.join(subpath, f"plot_quiver_{datetimestr}.jpg"),
            "tmp_name": os.path.join(subpath, "OUTPUT/plot_quiver.jpg"),
        }

    }
    # output_files = OUTPUT_FILES_ALL
    input_files = {
        "videofile": models.File(
            remote_name=str(instance.file),
            tmp_name=str(instance.file)
        )
    }
    subtasks = get_subtasks(instance, output_files=output_files)
    callbacks = []
    # callbacks = get_callbacks(
    #     instance.camera_config,
    #     query_callbacks
    # )

    task = models.Task(
        subtasks=subtasks,
        input_files=input_files,
        output_files=output_files,
        callbacks=callbacks,
        storage=storage
    )
    return task.to_json(serialize=serialize)


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

def get_storage(instance):
    """
    translates storage parameters into nodeodm Storage object

    Parameters
    ----------
    storage

    Returns
    -------

    """

    if "FileSystemStorage" in str(instance.file.storage):
        file_path = instance.file.path.split(str(instance.file))[0]
        url, bucket_name = os.path.split(os.path.normpath(file_path))
        storage_data = {
            "url": url,
            "bucket_name": bucket_name
        }
    else:
        storage_options = settings.STORAGES["media"]["OPTIONS"]
        storage_data = {
            "url": storage_options["endpoint_url"],
            "bucket_name":  storage_options["bucket_name"],
            "options": {
                "access_key": storage_options["access_key"],
                "secret_key": storage_options["secret_key"],
            }
        }

    storage = models.get_storage(
        **storage_data
    )
    return storage


def get_subtasks_form(instance):
    camera_config = instance
    video = None
    subtask = get_subtask_all(
        camera_config=camera_config,
        video=video
    )
    return [subtask]


def get_subtasks(instance, output_files=OUTPUT_FILES_ALL):
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
    error_msg = "No water level or time series associated with video"
    if not instance.time_series:
        raise Exception(error_msg)
    if not instance.time_series.h:
        raise Exception(error_msg)
    camera_config = instance.camera_config
    video = instance
    if not camera_config.recipe:
        raise Exception("Cannot create task, no recipe available")
    # we assume first that only 2d is processed
    task_type = "2d_only"
    # check if we can do a full processing with 1d included. This requires camera profile and a transect section in the
    # recipe
    if camera_config.profile and "transect" in camera_config.recipe.data:
        task_type = "all"

    # now dependent on the available data, prepare a task
    if task_type == "all":
        subtask = get_subtask_all(camera_config=camera_config, video=video, output_files=output_files)
    else:
        raise NotImplementedError(
            "2D only tasks are not yet supported. Add a profile to the Camera Config to allow for processing this task."
        )
    # we provide a list back so that we can later extend this to hold several subtasks, e.g. one per cross section
    # if we have more than one.
    return [subtask]


def get_callbacks(instance, query_callbacks):
    callbacks = [getattr(callback_utils, c)(instance) for c in query_callbacks]
    return callbacks


def get_subtask_all(
        camera_config,
        video,
        output_files=OUTPUT_FILES_ALL
):
    """
    Makes a full subtask using the entire recipe, including getting profiles ready for processing where needed

    Parameters
    ----------
    camera_config
    video

    Returns
    -------

    """

    name = "velocity_flow_subprocess"
    cameraconfig = camera_config.camera_config
    recipe = camera_config.recipe.data
    profile = camera_config.profile.data
    if video:
        h_a = video.time_series.h
        videofile = str(video.file)
        input_files = {
            "videofile": {
                "remote_name": str(video.file),
                "tmp_name": str(video.file)
            }
        }
    else:
        h_a = -9999.0  # placeholder for real water level
        videofile = "video.mp4"  # placeholder for real water level
        input_files = {
            "videofile": {
                "remote_name": "video.mp4",
                "tmp_name": "video.mp4"
            }
        }
    # remove the geojson and shapefile parts
    recipe = recipe_update_profile(recipe, profile)

    # TODO: input_files should refer to name of file only (now full subpath to MEDIA_ROOT). Location is arranged by the Storage
    # define the subtask
    kwargs = {
        "videofile": videofile,
        "h_a": h_a,
        "cameraconfig": cameraconfig,
        "recipe": recipe,
        # "output": os.path.dirname(videofile),
        "output": os.path.join(settings.TEMP_FOLDER, os.path.dirname(videofile), "OUTPUT"),
        # "output": "./tmp/OUTPUT",  # TODO revisit this so it is not dependent on the tmp location
        "prefix": ""
    }
    subtask = models.Subtask(
        name=name,
        kwargs=kwargs,
        input_files=input_files,
        output_files=output_files
    )
    return subtask



def recipe_update_profile(recipe, profile):
    """
    Replaces any profile related information in the recipe with the provided profile instance.
    The routine checks this in the "transect"  section, where profile data is defined, and in the "plot"
    section, where one or several plots are defined as output.

    Parameters
    ----------
    recipe : dict
        containing a pyorc recipe as json
    profile : dict
        geojson with profile data

    Returns
    -------
    recipe : dict
        updated recipe

    """
    transect_template = recipe["transect"]
    transect = {}
    trans_no = 0

    for k, v in transect_template.items():
        # the transect section can contain a "write" directive (i.e. write to file)
        if k != "write":
            trans_no += 1
            # remove geojson or shapefile if they exist
            if "geojson" in v:
                del v["geojson"]
            if "shapefile" in v:
                del v["shapefile"]
            # replace the geojson for the profile values
            v["geojson"] = profile
            # replace the transect data
            transect[f"transect_{trans_no}"] = v
            # we only support one transect for now, so here we break. We may alter this when multiple transects
            # are attractive to retrieve.
            break
    # force the writer for transect to be true, this means data will be written to disk
    transect["write"] = True
    # replace the transect component with the updates
    recipe["transect"] = transect

    # now check the plot section
    if "plot" in recipe:
        # there can be multiple plots under the plot section, loop over all of them
        for k, v in recipe["plot"].items():
            if "transect" in v:
                transect = {}
                transect_template = v["transect"]
                for n, (k_, v_) in enumerate(transect_template.items()):
                    transect[f"transect_{n + 1}"] = v_
                    break
                # replace the transect information in the plot
                v["transect"] = transect
            # put back the plot into the upper dictionary, only changes something if a transect was found
            recipe["plot"][k] = v

    return recipe


def get_callback_url(request):
    """
    Dynamically generates the main end point with token where any sub callback should go to

    Returns
    -------

    """
    # get the end point for retrieving refresh tokens once expired
    token_refresh_end_point = reverse('api:token_refresh')
    url = request.build_absolute_uri("/")
    # collect refresh tokens for the requesting user
    tokens = get_tokens_for_user(request.user)
    if url[0:4] != "http":
        # try to add http to the url to ensure pydantic validates it.
        url = "http://" + url
    # TODO replace once we make a real create_task call
    callback_url = models.callback_url.CallbackUrl(
        url=url,
        token_refresh_end_point=token_refresh_end_point,
        **tokens
    )
    return callback_url

def get_callback_discharge_patch(instance):
    """
    Creates callback for patching the time_series instance attached to video with discharge values

    Parameters
    ----------
    instance : Video model instance

    Returns
    -------
    callback : nodeorc.models.Callback object

    """
    return models.Callback(
        func_name="discharge",
        request_type="PATCH",
        endpoint=reverse(
            "api:site-timeseries-detail",
            args=([
                str(instance.camera_config.site.id),
                str(instance.time_series.id)
            ])
        )
    )


def get_callback_video_patch(instance):
    return models.Callback(
        func_name="video",
        request_type="PATCH",
        kwargs={
            "camera_config": instance.camera_config.id
        },
        endpoint=reverse(
            "api:site-video-detail",
            args=([
                str(instance.camera_config.site.id),
                str(instance.id)
            ])
        )
    )



