# -*- python -*-
# ex: set filetype=python:

import os.path
from typing import Any

from buildbot.changes.changes import Change
from buildbot.plugins import reporters, schedulers, util, worker
from buildbot.reporters.message import MessageFormatter

from director.build_factory import (build_factory, checkout_step,
                                    default_step_kwargs)
from director.env import env, get_env
from director.github_hook import PRGithubEventHandler
from director.scummvm_reporter import JSONMessageFormatter, WebHookReporter
from director.steps import GenerateStartMovieCommands, download_step
from director.targets import generate_builder, test_targets

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
c["workers"] = [
    worker.LocalWorker("director-worker", max_builds=int(env["MAX_BUILDS"]))
]

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


def file_is_director_related(change: Change) -> bool:
    """True when the changed file is director related."""
    checks = ["engines/director", "graphics/macgui"]
    for name in change.files:
        for check in checks:
            if check in name:
                return True
    return False


####### BUILDER NAMES
lingo_builder = "lingotests"
builder_names = [lingo_builder]
builder_names.extend(target.builder_name for target in test_targets)

force_builder_names = ["build", *builder_names]

####### SCHEDULERS

# Configure the Schedulers, which decide how to react to incoming changes.  In this
# case, just kick off a 'runtests' build
build_scheduler = schedulers.SingleBranchScheduler(
    name="all",
    change_filter=util.ChangeFilter(repository="https://github.com/scummvm/scummvm"),
    treeStableTimer=5,
    fileIsImportant=file_is_director_related,
    builderNames=["build"],
)

director_scheduler = schedulers.Triggerable(
    name="Director Tests", builderNames=builder_names
)

force_scheduler = schedulers.ForceScheduler(
    name="force", builderNames=force_builder_names
)

c["schedulers"] = []
c["schedulers"].append(build_scheduler)
c["schedulers"].append(director_scheduler)
c["schedulers"].append(force_scheduler)

####### BUILDERS

# The 'builders' list defines the Builders, which tell Buildbot how to perform a build:
# what steps, and which workers can execute them.  Note that any particular build will
# only take place on one worker.

build_lock = util.MasterLock("Build")


c["builders"] = []
c["builders"].extend(generate_builder(target) for target in test_targets)
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

lingo_directory = "./engines/director/lingo/tests/"
lingo_factory.addStep(
    GenerateStartMovieCommands(
        directory=lingo_directory,
        game_id="directortest",
        name="Generate lingo test commands",
        command=["find", lingo_directory, "-name", "*.lingo", "-printf", "%P\n"],
        haltOnFailure=True,
        **default_step_kwargs,
    )
)

c["builders"].append(
    util.BuilderConfig(
        name=lingo_builder, workernames=["director-worker"], factory=lingo_factory
    )
)

####### BUILDBOT SERVICES

# 'services' is a list of BuildbotService items like reporter targets. The
# status of each build will be pushed to these targets. buildbot/reporters/*.py
# has a variety to choose from, like IRC bots.

c["services"] = []

if env["DISCORD_WEBHOOK"]:
    scummvm_reporter = WebHookReporter(
        env["DISCORD_WEBHOOK"],
        mode="changesteps",
        messageFormatter=JSONMessageFormatter(),
    )
    c["services"].append(scummvm_reporter)

# RTS: Roland Test Server
if get_env("RTS_DISCORD_WEBHOOK"):
    slack_webhook = reporters.SlackStatusPush(endpoint=get_env("RTS_DISCORD_WEBHOOK"))
    c["services"].append(slack_webhook)

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
        console_view={},
        grid_view={},
        badges={"left_pad": 0, "right_pad": 0, "border_radius": 3, "style": "badgeio"},
    ),
    change_hook_dialects={
        "github": {
            "secret": env["GITHUB_WEBHOOK_SECRET"],
            "strict": True,
            "class": PRGithubEventHandler,
        }
    },
    allowed_origins=["*"],
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
