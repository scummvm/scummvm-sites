# -*- python -*-
# ex: set filetype=python:

import os.path
from typing import Any

from buildbot.changes.changes import Change
from buildbot.plugins import reporters, schedulers, util, worker

from build_factory import build_factory, checkout_step, default_step_kwargs
from env import env, get_env
from scummvm_reporter import ScummVMDirectorReporter
from steps import GenerateStartMovieCommands, download_step

# This is a sample buildmaster config file. It must be installed as
# 'master.cfg' in your buildmaster's base directory.

# This is the dictionary that the buildmaster pays attention to. We also use
# a shorter alias to save typing.
c: Any
BuildmasterConfig: Any
c = BuildmasterConfig = {}

####### SECRETS
# We don't use a secretsProvider. It wouldn't work together with
# the reporters.

####### WORKERS

# The 'workers' list defines the set of recognized workers. Each element is
# a Worker object, specifying a unique worker name and password.  The same
# worker name and password must be configured on the worker.
c["workers"] = [worker.LocalWorker("director-worker", max_builds=3)]

# 'protocols' contains information about protocols which master will use for
# communicating with workers. You must define at least 'port' option that workers
# could connect to your master with this protocol.
# 'port' must match the value configured into the workers (with their
# --master option)
c["protocols"] = {"pb": {"port": 9989}}

####### CHANGESOURCES

# the 'change_source' setting tells the buildmaster how it should find out
# about source code changes.  Here we point to the buildbot version of a python hello-world project.

# leave empty, the github hook should take care of it.
c["change_source"] = []


build_lock = util.MasterLock("Build")

# check if test files are available:
D4_TEST_DIR = env["D4_TEST_DIR"]
CHOP_SUEY_DIR = env["CHOP_SUEY_DIR"]

# Declare builder names
D4_builder = "D4tests"
CS_builder = "Chop Suey Tests"
Lingo_builder = "lingotests"


def file_is_director_related(change: Change) -> bool:
    """True when the changed file is director related."""
    checks = ["engines/director", "graphics/macgui"]
    for name in change.files:
        for check in checks:
            if check in name:
                return True
    return False


####### SCHEDULERS

# Configure the Schedulers, which decide how to react to incoming changes.  In this
# case, just kick off a 'runtests' build


build_scheduler = schedulers.SingleBranchScheduler(
    name="all",
    change_filter=util.ChangeFilter(repository="https://github.com/scummvm/scummvm"),
    treeStableTimer=None,
    fileIsImportant=file_is_director_related,
    builderNames=["build"],
)

builder_names = [Lingo_builder]
if D4_TEST_DIR:
    builder_names.append(D4_builder)
if CHOP_SUEY_DIR:
    builder_names.append(CS_builder)

lingo_scheduler = schedulers.Triggerable(
    name="Director Tests", builderNames=builder_names
)

c["schedulers"] = []
c["schedulers"].append(build_scheduler)
c["schedulers"].append(lingo_scheduler)

force_builder_names = ["build", Lingo_builder]
if D4_TEST_DIR:
    force_builder_names.append(D4_builder)
if CHOP_SUEY_DIR:
    force_builder_names.append(CS_builder)

if env["ENABLE_FORCE_SCHEDULER"]:
    c["schedulers"].append(
        schedulers.ForceScheduler(name="force", builderNames=force_builder_names)
    )

####### BUILDERS

# The 'builders' list defines the Builders, which tell Buildbot how to perform a build:
# what steps, and which workers can execute them.  Note that any particular build will
# only take place on one worker.


c["builders"] = []


if D4_TEST_DIR:
    test_factory = util.BuildFactory()
    test_factory.addStep(download_step)
    test_factory.addStep(
        GenerateStartMovieCommands(
            name="Generate D4 test commands",
            command=["cat", os.path.join(D4_TEST_DIR, "test_scripts.txt")],
            haltOnFailure=True,
            directory=D4_TEST_DIR,
            target="--auto-detect",
            debugflags="fewframesonly,fast",
            **default_step_kwargs,
        )
    )
    c["builders"].append(
        util.BuilderConfig(
            name=D4_builder, workernames=["director-worker"], factory=test_factory
        )
    )

if CHOP_SUEY_DIR:
    test_factory = util.BuildFactory()
    test_factory.addStep(download_step)
    test_factory.addStep(
        GenerateStartMovieCommands(
            name="Generate Chop Suey test commands",
            command=["find", CHOP_SUEY_DIR, "-name", "*.dir"],
            haltOnFailure=True,
            directory=CHOP_SUEY_DIR,
            target="--auto-detect",
            debugflags="fewframesonly,fast,bytecode",
            **default_step_kwargs,
        )
    )
    c["builders"].append(
        util.BuilderConfig(
            name=CS_builder, workernames=["director-worker"], factory=test_factory
        )
    )

c["builders"].append(
    util.BuilderConfig(
        name="build",
        workernames=["director-worker"],
        factory=build_factory,
        locks=[build_lock.access("exclusive")],
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
        **default_step_kwargs,
    )
)

c["builders"].append(
    util.BuilderConfig(
        name=Lingo_builder, workernames=["director-worker"], factory=lingo_factory
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
    discord_webhook = ScummVMDirectorReporter(endpoint=get_env("DISCORD_WEBHOOK"))
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
    port=5000,
    plugins=dict(
        waterfall_view={},
        console_view={},
        grid_view={},
        badges={"left_pad": 0, "right_pad": 0, "border_radius": 3, "style": "badgeio"},
    ),
    change_hook_dialects={"github": {"secret": env["GITHUB_WEBHOOK_SECRET"]}},
)

c["www"]["auth"] = util.GitHubAuth(
    env["GITHUB_CLIENT_ID"],
    env["GITHUB_CLIENT_SECRET"],
    apiVersion=4,
    getTeamsMembership=True,
)

c["www"]["authz"] = util.Authz(
    allowRules=[util.AnyControlEndpointMatcher(role="developers"),],
    roleMatchers=[util.RolesFromGroups(groupPrefix="scummvm/")],
)


####### DB URL
c["db"] = {
    # This specifies what database buildbot uses to store its state.
    # It's easy to start with sqlite, but it's recommended to switch to a dedicated
    # database, such as PostgreSQL or MySQL, for use in production environments.
    # http://docs.buildbot.net/current/manual/configuration/global.html#database-specification
    "db_url": env["DATABASE_URL"],
}
