from api import __version__


def version_processor(request):
    return {
        "APP_VERSION": __version__
    }