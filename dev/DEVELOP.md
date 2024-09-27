# Developer instructions

## Rights
The [AGPL-3.0 license](https://github.com/localdevices/LiveORC/blob/main/LICENSE) applies to all contributions made to 
this project. By contributing you agree to these license 
terms.

## Reporting issues
LiveORC is a highly active and new project. Therefore, we welcome reports of bugs, problems with features, and even 
suggestions for new features, ideally with opportunities to get their implementation funded. However, before 
submitting an issue, first assess existing, open and closed issues, before creating a new one.

For reports of bugs, please run liveorc in debug mode using `--debug` as additional option in the `./liveorc.sh` 
launching script and provide tracebacks. Minimal reproducible examples with data may be very helpful if there is an 
issue with video files. 

## Checklist for pull requests

If you wish to fix a bug or implement a feature, please make sure to go through the following steps:

1. If it does not yet exist, create an issue following the template. We highly recommend to first await a discussion 
   with a localdevices team member before you start developing.
2. Create a fork of the code where you develop your improvements.
3. Update `dev/CHANGELOG.md` with a summary of your changes and a link to your pull request.
4. Push your commits to your fork and open a draft pull request. Please fill in the pre-filled template with all 
   relevant information. Update your pull request if needed to complete the checklist.
5. Once you are satisfied with the changes mark the pull as "ready for review". A localdevices team member will 
   review your contributions and may request improvements.
6. Once the review is accepted, the localdevices team member will merge your contributions in the main branch.

## Release checklist

Before creating a new release, the following MUST be in place.

- Bump version number (minor: fixes and bugs, medium: small changes in API, added features, major: large breaking 
  changes or major new options and features)
- Update `CHANGELOG.md`.
- ensure any new requirements are added to `dev/requirements.txt` without a version number (unless a specific 
  version is required).
- freeze `requirements.txt` as instructed below.

## How to freeze packages

This requires a clean setup of the entire environment as follows:

```shell
# create and activate a fresh venv
python -m venv $HOME/venv/liveorc-dev
source $HOME/venv/liveorc-dev/bin/activate
pip install --upgrade pip
pip install -r dev/requirements.txt
# run the tests, do not deploy before these are satisfactory
python manage.py test
# freeze only packages directly imported into the project
pip freeze -q -r dev/requirements.txt | sed '/freeze/,$ d' > requirements.txt
deactivate
# remove temporarily created venv
rm -fr $HOME/venv/liveorc-dev

```
> [!NOTE]
> As shown above, ensure that all tests run satisfactorily. This requires an installation on python<3.12, tests fail with
> python=3.12 because the `assertEquals` changed name. It is recommended to also check if the tests of the installed 
> version of pyopenrivercam are running without faults, by checking out the code of pyorc from 
> https://github.com/localdevices/pyorc and running the tests with the installed liveorc environment.
