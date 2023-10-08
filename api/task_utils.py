from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.urls import reverse
# helper functions to develop tasks from models
from nodeorc import models

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


def get_task(instance, request, serialize=True, *args, **kwargs):
    """
    Make a full task dict from the current video

    Parameters
    ----------
    instance

    Returns
    -------

    """
    callback_url = get_callback_url(request)
    # TODO connect storage once agnostic storage solutions implemented
    storage = get_storage(instance)
    subtasks = get_subtasks(instance)
    output_files = OUTPUT_FILES_ALL
    task = models.Task(
        callback_url=callback_url,
        storage=storage,
        subtasks=subtasks,
        output_files=output_files
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
    url = settings.MEDIA_ROOT
    bucket_name = reverse(
        "api:site-video-detail",
        args=([str(instance.camera_config.site.id), str(instance.id)])
    )

    return models.Storage(
        url=url,
        bucket_name=bucket_name
    )
    # TODO: make storage agnostic for cloud storage options

def get_subtasks(instance):
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
    if not(instance.time_series):
        raise Exception(error_msg)
    if not(instance.time_series.h):
        raise Exception(error_msg)
    if not(instance.camera_config.recipe):
        raise Exception("Cannot create task, no recipe available")
    # we assume first that only 2d is processed
    task_type = "2d_only"
    # check if we can do a full processing with 1d included. This requires camera profile and a transect section in the
    # recipe
    if instance.camera_config.profile and "transect" in instance.camera_config.recipe.data:
        task_type = "all"

    # now dependent on the available data, prepare a task
    if task_type == "all":
        subtask = get_subtask_all(instance)
    # we provide a list back so that we can later extend this to hold several subtasks, e.g. one per cross section
    # if we have more than one.
    return [subtask]



def get_subtask_all(instance):
    """
    Makes a full subtask using the entire recipe, including getting profiles ready for processing where needed

    Parameters
    ----------
    instance

    Returns
    -------

    """

    name = "velocity_flow_subprocess"
    cameraconfig = instance.camera_config.camera_config
    h_a = instance.time_series.h
    videofile = str(instance.file)
    recipe = instance.camera_config.recipe.data
    profile = instance.camera_config.profile.data
    # remove the geojson and shapefile parts
    recipe = recipe_update_profile(recipe, profile)

    # recipe is adapted to match profile, now prepare the callbacks

    callbacks = [
        get_callback_discharge_patch(instance),
        get_callback_video_patch(instance)
    ]
    # TODO: input_files should refer to name of file only (now full subpath to MEDIA_ROOT). Location is arranged by the Storage
    input_files = {
        "videofile": {
           "remote_name": str(instance.file),
            "tmp_name": str(instance.file)
        }
    }
    output_files = OUTPUT_FILES_ALL  # hard-coded output file names, typical for this task
    # define the subtask
    kwargs = {
        "videofile": videofile,
        "h_a": h_a,
        "cameraconfig": cameraconfig,
        "recipe": recipe,
        "output": "./tmp/OUTPUT",  # TODO revisit this so it is not dependent on the tmp location
        "prefix": ""
    }
    subtask = models.Subtask(
        name=name,
        kwargs=kwargs,
        callbacks=callbacks,
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

def callback():
    return models.Callback(
        func_name="post_discharge",
        kwargs={},
        callback_endpoint="/processing/examplevideo/discharge"  # used to extend the default callback url
    )

def get_tokens_for_user(user):
    """
    Retrieves access and refresh tokens for the user

    Parameters
    ----------
    user : User (django auth model instance)
        The user, typically the one currently logged in and making the request

    Returns
    -------
    tokens : dict
        containing "token_refresh": str and "token_access": str

    """
    refresh = RefreshToken.for_user(user)
    return {
        'token_refresh': str(refresh),
        'token_access': str(refresh.access_token),
    }


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