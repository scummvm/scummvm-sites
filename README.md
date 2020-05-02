# Buildbot for testing the SCUMMVM director engine

To run it, follow the tutorial from buildbot.net.
Install the python packages in a venv with pip install -r requirements.txt
Start a worker as done in the tutorial with a worker_password that's in the .env file.

To use the reporters the following variables, all strings, need to be placed in a .env file. AKA as DotEnv.
DATABASE_URL=sqlite:///state.sqlite
worker_password=
discord_webhook=
relay_host=
to_addr=
from_addr=
smtp_password=
D4_TEST_DIR= # can be empty, and won't be tested in that case.

## Github Oauth
There's an oauth application:
https://github.com/settings/applications/1281774

## Goal:
To run this online as a CI server and to give feedback about what regressions in our discord channel.

## Ideas
- only run when files director uses are changes. Can be done with the file attribute for 'Change' or fileIsImportant on schedular.
- make it easy to add extra scripts to the test buildr
- Dynamically figure out which D4 tests there are, in the same way as is done with lingo tests.
- D4 test files could be put on S3 storage.
- look at buildbot.process.factory.Trial: it has per test ouput, including reporting on changes between runs.
- make it easy to see how one can run the test themselves.
- Use github devs group authentication, or add a 'director/admin' group
- output the stderr to our google spreadsheet
- Move to poetry or pipenv for building it.
- Check out surpressionFile option for shell command, to use it for surpression of non Warnings.
- Show only failed in web overview.
- Check scummvm IRC reporter, it reports rather nicely.
- ask online: A testrun is done before a build.
- look into triggers instead of dependent: https://github.com/scummvm/scummvm-sites/blob/buildbot/config/master.cfg#L1698-L1700

## Bugs:
- discord /slack build number is not correct, Build #45 points to build 1 of a new builder type.
- It doesn't link to the github commits
- failures have a long list of responsible committers.
- Lingo tests ran on a newer checkout: specify the checkout hash of the source checkout in the lingo build.

## Production:

It runs on dokku: http://dokku.viewdocs.io/dokku/
installed at digital ocean.
Plugins required: postgres, letsencrypt dokku-apt

Buildpack installation:
dokku buildpacks:add buildbot https://github.com/moneymeets/python-poetry-buildpack.git
buildbot-dokku buildpacks:add buildbot heroku/python