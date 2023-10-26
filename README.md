# Buildbot for testing the SCUMMVM director engine

This buildbot runs scummvm on a multitude of Director 2, 3 and 4 files.
Failures and warnings help spot problem areas and regressions.

It's located at: https://john.scummvm.org/

## Installation:
install python poetry: https://python-poetry.org/
$ poetry install

Check the director/env.py file for a list of enviroment variables that are used.
These variables can be in a .env file that must be placed in the root of the project directory.
Note:
    The `director/env.py` file doesn't have all env keys which are in use.

## Goal:
To run this online as a CI server and to give feedback about what regressions in our discord channel.
This has been achieved. It reports changes on our discord channel.

## How to add a new test target:

- Create a directory with all the files to be tested,
- include a scummvm.conf with the game_id:
    cd /path/to/game && /path/to/scummvm -c scummvm.conf -p . --add
- in scummvm.conf: change the pathline to: path=.
- add an entry in targets.json
 {
        "name": "Spaceship Warlock",
        "directory": "warlock-win",
        "game_id": "warlock-win",
        "platform": "win",
        "version": "D3",
        "debugflags": "fewframesonly,fast",
        "movienames": ["moviename", ....]
 }


## wishlist:
- Add screenshot generation with automatic diffs: inspired by: https://fifo.ci/

## Run it yourself

Install python-poetry and run:
$ poetry install

To run buildbot:
$ buildbot start .

Open a browser: http://localhost:8010

## Wait for: All D5 targets
- Director 5 and higher
- Director dictionary 5-win: Crashes too much

## Improvements ideas

The most important improvement ideas are tracked in trello:
https://trello.com/b/iQxOkBvI/director

This serves as a placeholder for ideas that aren't ready

### enable developers to run the tests locally
- script that downloads the files
- runs the commands against it
- With and without dummy drivers

### other Ideas
- look at buildbot.process.factory.Trial: it has per test ouput, including reporting on changes between runs.
- make it easy to see how one can run the test themselves.
- Implement the `try` scheduler so that devs can test their changes
- Have test targets be dynamically generated, maybe in a test_scripts.json file in the test target.
- Run the tests for one target in parallel, or split out over multiple (virtual) test targets that get combined later

- Add a flag to only enable github auth in production
- Refactor lingo builder into targets, maybe upload/download the lingo directory so the checkout step isn't needed
- build our own dashboard to enable better reporting
    - Show builds per step, and be able to go to the previous output of the same step
    - see only failed steps
    - search all logs of a build for an occurance, or specific exit code
- PRs
    - report them on the PR page
    - only compare between master
    - don't compare new master run with the run with the PR
- Make buildbot API calls cachable
