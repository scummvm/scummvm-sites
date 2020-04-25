# -*- python -*-
# ex: set filetype=python:

import os.path

from buildbot.plugins import *
from steps import GenerateStartMovieCommands

from env import env, get_env

# This is a sample buildmaster config file. It must be installed as
# 'master.cfg' in your buildmaster's base directory.

# This is the dictionary that the buildmaster pays attention to. We also use
# a shorter alias to save typing.
c = BuildmasterConfig = {}

####### SECRETS
# We don't use a secretsProvider. It wouldn't work together with
# the reporters.

####### WORKERS

# The 'workers' list defines the set of recognized workers. Each element is
# a Worker object, specifying a unique worker name and password.  The same
# worker name and password must be configured on the worker.
c["workers"] = [worker.Worker("director-worker", get_env("worker_password"), max_builds=1)]

# 'protocols' contains information about protocols which master will use for
# communicating with workers. You must define at least 'port' option that workers
# could connect to your master with this protocol.
# 'port' must match the value configured into the workers (with their
# --master option)
c["protocols"] = {"pb": {"port": 9989}}

####### CHANGESOURCES

# the 'change_source' setting tells the buildmaster how it should find out
# about source code changes.  Here we point to the buildbot version of a python hello-world project.

c["change_source"] = []
c["change_source"].append(
    changes.GitPoller(
        "git://github.com/scummvm/scummvm/",
        workdir="gitpoller-workdir",
        branch="master",
        pollInterval=300,
    )
)

# check if D4 tests can be run:
D4_TEST_DIR = env["D4_TEST_DIR"]

####### SCHEDULERS

# Configure the Schedulers, which decide how to react to incoming changes.  In this
# case, just kick off a 'runtests' build


build_scheduler = schedulers.SingleBranchScheduler(
    name="all",
    change_filter=util.ChangeFilter(branch="master"),
    treeStableTimer=None,
    builderNames=["build"],
)

if D4_TEST_DIR:
    test_scheduler = schedulers.Dependent(
        name="D4 tests", upstream=build_scheduler, builderNames=["D4tests"]
    )

lingo_scheduler = schedulers.Dependent(
    name="scummvm Lingo tests", upstream=build_scheduler, builderNames=["lingotests"]
)

c["schedulers"] = []
c["schedulers"].append(build_scheduler)
c["schedulers"].append(lingo_scheduler)

force_builder_names = ["build", "lingotests"]
if D4_TEST_DIR:
    c["schedulers"].append(test_scheduler)
    force_builder_names.append("D4tests")

if env["ENABLE_FORCE_SCHEDULER"]:
    c["schedulers"].append(
        schedulers.ForceScheduler(
            name="force", builderNames=force_builder_names
        )
    )

####### BUILDERS

# The 'builders' list defines the Builders, which tell Buildbot how to perform a build:
# what steps, and which workers can execute them.  Note that any particular build will
# only take place on one worker.

default_step_kwargs = {"logEnviron": False}

build_factory = util.BuildFactory()
# check out the source
checkout_step = steps.GitHub(
    repourl="git://github.com/scummvm/scummvm.git", mode="incremental",
    **default_step_kwargs
)
build_factory.addStep(checkout_step)
# run the tests (note that this will require that 'trial' is installed)
build_factory.addStep(
    steps.Configure(
        command=["./configure", "--disable-all-engines", "--enable-engine=director",], **default_step_kwargs
    )
)
build_factory.addStep(steps.Compile(command=["make"], **default_step_kwargs))

master_dir = os.path.dirname(__file__)

worker_file = "scummvm"
master_file = os.path.join(master_dir, "scummvm-binary")

build_factory.addStep(steps.FileUpload(workersrc=worker_file, masterdest=master_file))

download_step = steps.FileDownload(
    mastersrc=master_file, workerdest=worker_file, mode=755,
)

if D4_TEST_DIR:
    test_factory = util.BuildFactory()
    test_factory.addSteps([download_step])

    f = open("test_scripts.txt", "r")
    test_scripts = f.read().split("\n")
    for test in test_scripts:
        test_factory.addStep(
            steps.Test(
                name=test,
                description=test,
                descriptionDone=test,
                command=[
                    "./scummvm",
                    "--debugflags=fewframesonly,fast",
                    "--auto-detect",
                    "-p",
                    env["D4_TEST_DIR"],
                    f"--start-movie={test}"
                ],
                env={"SDL_VIDEODRIVER": "dummy"},
                timeout=5,
                maxTime=10,
                **default_step_kwargs
            )
        )

lingo_factory = util.BuildFactory()
lingo_factory.addStep(checkout_step)
lingo_factory.addStep(download_step)

lingo_factory.addStep(
    GenerateStartMovieCommands(
        name="Generate lingo test commands",
        command=["find", "./engines/director/lingo/tests/", "-name", "*.lingo"],
        haltOnFailure=True,
        directory="./engines/director/lingo/tests/",
        target="directortest",
        **default_step_kwargs
    )
)


c["builders"] = []

if D4_TEST_DIR:
    c["builders"].append(
        util.BuilderConfig(
            name="D4tests", workernames=["director-worker"], factory=test_factory
        )
    )

c["builders"].append(
    util.BuilderConfig(
        name="build", workernames=["director-worker"], factory=build_factory
    )
)

c["builders"].append(
    util.BuilderConfig(
        name="lingotests", workernames=["director-worker"], factory=lingo_factory
    )
)

####### BUILDBOT SERVICES

# 'services' is a list of BuildbotService items like reporter targets. The
# status of each build will be pushed to these targets. buildbot/reporters/*.py
# has a variety to choose from, like IRC bots.

c["services"] = []

if get_env("relay_host"):
    mn = reporters.MailNotifier(
        fromaddr=get_env("from_addr"),
        sendToInterestedUsers=False,
        extraRecipients=[get_env("to_addr")],
        relayhost=get_env("relay_host"),
        smtpPort=587,
        smtpUser=get_env("from_addr"),
        smtpPassword=get_env("smtp_password"),
        useTls=True,
    )
    c["services"].append(mn)

# Use Discord's slack compatibility
if get_env("DISCORD_WEBHOOK"):
    discord_webhook = reporters.SlackStatusPush(
        endpoint=get_env("DISCORD_WEBHOOK")
    )
    c["services"].append(discord_webhook)

####### PROJECT IDENTITY

# the 'title' string will appear at the top of this buildbot installation's
# home pages (linked to the 'titleURL').

c["title"] = "Director builds"
c["titleURL"] = "https://github.com/scummvm/scummvm/"

# the 'buildbotURL' string should point to the location where the buildbot's
# internal web server is visible. This typically uses the port number set in
# the 'www' entry below, but with an externally-visible host name which the
# buildbot cannot figure out without some help.

c["buildbotURL"] = env["BUILDBOT_URL"]

# minimalistic config to activate new web UI
c["www"] = dict(
    port=5000, plugins=dict(waterfall_view={}, console_view={}, grid_view={})
)

####### DB URL

c["db"] = {
    # This specifies what database buildbot uses to store its state.
    # It's easy to start with sqlite, but it's recommended to switch to a dedicated
    # database, such as PostgreSQL or MySQL, for use in production environments.
    # http://docs.buildbot.net/current/manual/configuration/global.html#database-specification
    "db_url": env["DATABASE_URL"],
}
