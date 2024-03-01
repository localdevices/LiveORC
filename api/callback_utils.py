from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from nodeorc import models


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


def get_base_url(request):
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


def get_task_callback_discharge_patch(instance):
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
        ),
        file="transect"
    )


def get_form_callback_discharge_post(instance):
    """
    Creates callback for patching the time_series instance attached to video with discharge values

    Parameters
    ----------
    instance : Camera Config model instance

    Returns
    -------
    callback : nodeorc.models.Callback object

    """
    return models.Callback(
        func_name="discharge",
        request_type="POST",
        endpoint=reverse(
            "api:site-timeseries-list",
            args=([
                str(instance.site.id),
            ])
        ),
        file="transect"
    )


def get_form_callback_video_post(instance):
    return models.Callback(
        func_name="video",
        request_type="POST",
        kwargs={
            "camera_config": instance.id
        },
        endpoint=reverse(
            "api:video-list",
        ),
        files_to_send=["jpg"]
    )


def get_form_callback_video_no_file_post(instance):
    return models.Callback(
        func_name="video_no_file",
        request_type="POST",
        kwargs={
            "camera_config": instance.id
        },
        endpoint=reverse(
            "api:video-list",
        ),
        files_to_send=["jpg"]

    )


def get_task_callback_video_patch(instance):
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
        ),
        files_to_send=["jpg"]
    )

