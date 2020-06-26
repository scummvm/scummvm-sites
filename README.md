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

## How to add a new test target:

Adding new test targets is done via these steps:
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
    git push dokku director-buildbot:master

## Work on:
- diff highlighting
- compare to latest master

## wishlist:
- Use 'diff' syntax highlighting when reporting
- Add screenshot generation with automatic diffs: inspired by: https://fifo.ci/

## Run it yourself

Install python-poetry and run:
$ poetry install

To run buildbot:
$ buildbot start . 

Open a browser: http://localhost:5000

## To install it yourself on a server

It runs on dokku: http://dokku.viewdocs.io/dokku/
installed at digital ocean.
Plugins required: postgres, letsencrypt, dokku-apt, dokku-nginx-stream

Buildpack installation:
dokku buildpacks:add buildbot https://github.com/moneymeets/python-poetry-buildpack.git
dokku buildpacks:add buildbot heroku/python

git remote add dokku hostname:buildbot

## Wishlist of GAMES to add
- D4 guided tours
- warlock mac
- warlock demo mac
- warlock demo win
- JMAN mac (implement recursive hcopy tool)
- majestic mac

## Wait for: All D5 targets
- Director 5 and higher
- Director dictionary 5-win: Crashes too much

## Spin up a test server
The scripts in the test-deploy directory can be leveraged to 
spin up a buildbot test instance.


## Improvements ideas

The most important improvement ideas are tracked in trello:
https://trello.com/b/iQxOkBvI/director

This serves as a placeholder for ideas that aren't ready 

### remove friction for adding new targets
- Put all files on external storage
- put target configuration into json
- just require a reconfig for buildbot to reload the json
- sync files from external storage for builders

1) Move to JSON configuration 
  {  
    name: str 
    game_id: str # could be in mandatory scummvm.conf   
    platform: str = OneOf("win", "mac")
    version: str = OneOf("D2", "D3", "D4")
    debugflags: str = "fewframesonly,fast" # at least "fewframesonly,fast" # for >= D4 include bytecode
    files: [str] = ["file1", "file2", "etc..."]
  }

### enable developers to run the tests locally
- script that downloads the files
- runs the commands against it
- With and without dummy drivers

### other Ideas
- Put game test files on S3 storage
- look at buildbot.process.factory.Trial: it has per test ouput, including reporting on changes between runs.
- make it easy to see how one can run the test themselves.
- Implement the `try` scheduler so that devs can test their changes
- Have test targets be dynamically generated, maybe in a test_scripts.json file in the test target.
- Run the tests for one target in parallel, or split out over multiple (virtual) test targets that get combined later

- Add a flag to only enable github auth in production
- Refactor lingo builder into targets, maybe upload/download the lingo directory so the checkout step isn't needed
- Add maintenance "janitor" that cleans up old logs from the db
- build our own dashboard to enable better reporting
    - Show builds per step, and be able to go to the previous output of the same step
    - see only failed steps
    - search all logs of a build for an occurance, or specific exit code
- PRs
    - report them on the PR page
    - only compare between master
    - don't compare new master run with the run with the PR
- Make buildbot output cachable