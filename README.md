# Buildbot for testing the SCUMMVM director engine

This buildbot runs scummvm on a multitude of Director 2, 3 and 4 files.
Failures and warnings help spot problem areas and regressions.

It's located at: https://buildbot.projecttycho.nl

## Installation:
install python poetry: https://python-poetry.org/
$ poetry install

Check the director.env file for a list of enviroment variables that are used.
These variables can be in a .env file that must be placed in the root of the project directory.

## Goal:
To run this online as a CI server and to give feedback about what regressions in our discord channel.

This has been achieved. It reports changes on our discord channel.
A stretch goal is to show changes in buildsteps, instead of a full build.

## How to add a new test target:

Adding new test targets is easy:
- Create a directory with all the files to be tested,
- put a `test_scripts.txt` file in the root of that directory,
    - with all files that need to be tested,
    - one line per file and
    - with the path to that file: e.g. a/FILE.MMM
- add a TestTarget in `director.targets:available_test_targets`
- add the variable that contains the path to the directory of test files in `director.env:default_vars`.

## Deploy

It runs on dokku. To add the remote:
    git remote add dokku dokku@buildbot.projecttycho.nl:buildbot

To deploy::
    git push dokku

## Ideas
- Put game test files on S3 storage
- Add remote builders
- look at buildbot.process.factory.Trial: it has per test ouput, including reporting on changes between runs.
- make it easy to see how one can run the test themselves.
- Implement the `try` scheduler so that devs can test their changes
- Extend githubPoller with files in the Change
- Add more builders
- Have test targets be dynamically generated, maybe in a test_scripts.json file in the test target.
- Run the tests for one target in parallel, or split out over multiple (virtual) test targets that get combined later
- Add screenshot generation with automatic diffs: inspired by: https://fifo.ci/
- Add a flag to only enable github auth in production
- Refactor lingo builder into targets, maybe upload/download the lingo directory so the checkout step isn't needed

## Bugs:
- doesn't run on PullRequests: We only build on changed director and macgui file, and the github poller doesn't include changed files for PRs.

## To install it yourself on a server

It runs on dokku: http://dokku.viewdocs.io/dokku/
installed at digital ocean.
Plugins required: postgres, letsencrypt dokku-apt

Buildpack installation:
dokku buildpacks:add buildbot https://github.com/moneymeets/python-poetry-buildpack.git
buildbot-dokku buildpacks:add buildbot heroku/python

## Wishlist of GAMES to add
- warlock mac
- warlock demo mac
- warlock demo win
- mediaband
- majestic mac
- Appartment D2
- Appartment D3
- Appartment D4

## Wait for: All D5 targets
- Director 5 and higher
- Director dictionary 5-win: Crashes too much