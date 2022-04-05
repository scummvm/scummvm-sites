# -*- python -*-
# ex: set filetype=python:

from typing import Any
from datetime import timedelta

from buildbot.changes.changes import Change
from buildbot.plugins import reporters, schedulers, util, worker
from twisted.python import log
from environs import Env

from director.build_factory import build_factory
from director.lingo_factory import lingo_factory
from director.scummvm_reporter import JSONMessageFormatter, WebHookReporter
from director.targets import generate_builder, test_targets

# This is a sample buildmaster config file. It must be installed as
# 'master.cfg' in your buildmaster's base directory.

# This is the dictionary that the buildmaster pays attention to. We also use
# a shorter alias to save typing.
c: Any
BuildmasterConfig: Any
c = BuildmasterConfig = {}

env = Env()
env.read_env()

####### SECRETS
# We don't use a secretsProvider. It wouldn't work together with
# the reporters.

####### MultiMaster

c["multiMaster"] = env.bool("MULTI_MASTER", False)

WORKER_NAMES = env.list("WORKER_NAMES")

####### WORKERS

# The 'workers' list defines the set of recognized workers. Each element is
# a Worker object, specifying a unique worker name and password.  The same
# worker name and password must be configured on the worker.
HAS_WORKER = env.bool("HAS_WORKER", False)
IS_LOCAL_WORKER = env.bool("IS_LOCAL_WORKER", False)
if HAS_WORKER:
    c["workers"] = []
    scummvm_builbot_password = env("SCUMMVM_BUILDBOT_PASSWORD")
    for worker_name in WORKER_NAMES:
        c["workers"].append(
            worker.Worker(
                worker_name, scummvm_builbot_password, max_builds=env.int("MAX_BUILDS", 12)
            )
        )
elif IS_LOCAL_WORKER:
    c["workers"] = []
    worker_name = "director-worker"
    c["workers"].append(
        worker.LocalWorker(worker_name, max_builds=env.int("MAX_BUILDS", 3))
    )

# 'protocols' contains information about protocols which master will use for
# communicating with workers. You must define at least 'port' option that workers
# could connect to your master with this protocol.
# 'port' must match the value configured into the workers (with their
# --master option)

c["protocols"] = {"pb": {"port": env.int("PROTOCOLS_PORT", 9989)}}

####### SCHEDULERS

# Configure the Schedulers, which decide how to react to incoming changes.  In this
# case, just kick off a 'runtests' build


def file_is_director_related(change: Change) -> bool:
    """True when the changed file is director related."""
    checks = ["engines/director", "graphics/macgui"]

    log.msg("###################### CHANGE")
    log.msg(f"{change}")
    for name in change.files:
        for check in checks:
            if check in name:
                return True
    return False

REPOSITORY = env("REPOSITORY", "https://github.com/scummvm/scummvm")
####### BUILDER NAMES
lingo_builder = "lingotests (D4)"
builder_names = [lingo_builder]
if env.bool(
    "FULL_BUILD", True
):  # Set FULL_BUILD to false to get a quicker lingo only build
    builder_names.extend(target.builder_name for target in test_targets)

force_builder_names = ["build", *builder_names]

build_scheduler = schedulers.SingleBranchScheduler(
    name="all",
    change_filter=util.ChangeFilter(repository=REPOSITORY),
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

if HAS_WORKER or IS_LOCAL_WORKER:
    build_lock = util.MasterLock("Build")

    c["builders"] = []
    c["builders"].append(
        util.BuilderConfig(
            name="build",
            workernames=[WORKER_NAMES[0]],
            factory=build_factory,
            locks=[build_lock.access("exclusive")],
        )
    )

    c["builders"].append(
        util.BuilderConfig(
            name=lingo_builder, workernames=WORKER_NAMES, factory=lingo_factory
        )
    )

    if env.bool(
        "FULL_BUILD", True
    ):
        c["builders"].extend(
            generate_builder(target, WORKER_NAMES) for target in test_targets
        )

####### CHANGESOURCES

# the 'change_source' setting tells the buildmaster how it should find out
# about source code changes.  Here we point to the buildbot version of a python hello-world project.

# leave empty, the github hook should take care of it.
c["change_source"] = []

####### BUILDBOT SERVICES

# 'services' is a list of BuildbotService items like reporter targets. The
# status of each build will be pushed to these targets. buildbot/reporters/*.py
# has a variety to choose from, like IRC bots.

c["services"] = []

c["buildbotURL"] = env("BUILDBOT_URL")
WEB_UI = env.bool("WEB_UI", True)
if WEB_UI:
    DISCORD_WEBHOOK = env("DISCORD_WEBHOOK")
    scummvm_reporter = WebHookReporter(
        DISCORD_WEBHOOK,
        mode="changesteps",
        messageFormatter=JSONMessageFormatter(),
    )
    c["services"].append(scummvm_reporter)

    # RTS: Roland Test Server
    RTS_DISCORD_WEBHOOK = env("RTS_DISCORD_WEBHOOK", "")
    if RTS_DISCORD_WEBHOOK:
        slack_webhook = reporters.SlackStatusPush(endpoint=RTS_DISCORD_WEBHOOK)
        c["services"].append(slack_webhook)

    github_hook = {
        "secret": env("GITHUB_WEBHOOK_SECRET"),
        "strict": True,
        "pullrequest_ref": "head",
    }


    github_token = env("GITHUB_TOKEN")
    if github_token:
        github_hook["token"] = github_token

    ####### PROJECT IDENTITY

    # the 'title' string will appear at the top of this buildbot installation's
    # home pages (linked to the 'titleURL').

    c["title"] = "Director builds"
    c["titleURL"] = REPOSITORY

    # the 'buildbotURL' string should point to the location where the buildbot's
    # internal web server is visible. This typically uses the port number set in
    # the 'www' entry below, but with an externally-visible host name which the
    # buildbot cannot figure out without some help.

    #c["buildbotURL"] = "https://john-test.scummvm.org/"

    # minimalistic config to activate new web UI
    c["www"] = dict(
        port=env("WEB_UI_CONNECTION", "tcp:5000:interface=127.0.0.1"),
        plugins=dict(console_view={}, grid_view={},),
        change_hook_dialects={"github": github_hook},
        allowed_origins=["*"],
    )

    c["www"]["auth"] = util.GitHubAuth(
        env("GITHUB_CLIENT_ID"),
        env("GITHUB_CLIENT_SECRET"),
        apiVersion=4,
        getTeamsMembership=True,
    )

    c["www"]["authz"] = util.Authz(
        allowRules=[util.AnyControlEndpointMatcher(role="developers"),],
        roleMatchers=[util.RolesFromGroups(groupPrefix="scummvm/")],
    )
    c['www']['ui_default_config'] = { 
        'Grid.buildFetchLimit': 200,
    }
    c["configurators"] = [
        util.JanitorConfigurator(logHorizon=timedelta(weeks=5), hour=23, dayOfWeek=0)
    ]

if env.bool("WAMP", False):
    c['mq'] = {
        'type' : 'wamp',
        'router_url': env("WAMP_URL", 'ws://localhost:8080/ws'),
        'realm': 'realm1',
        # valid are: none, critical, error, warn, info, debug, trace
        #'wamp_debug_level' : 'error'
        'wamp_debug_level' : 'warn'
}


####### DB URL
c["db"] = {
    # This specifies what database buildbot uses to store its state.
    # It's easy to start with sqlite, but it's recommended to switch to a dedicated
    # database, such as PostgreSQL or MySQL, for use in production environments.
    # http://docs.buildbot.net/current/manual/configuration/global.html#database-specification
    "db_url": env("DATABASE_URL", default="sqlite:///state.sqlite"),
}

### disable sending usage data to buildbot. Their usage data receiver is down.
c["buildbotNetUsageData"] = None

### Use internal caching
# https://docs.buildbot.net/2.8.4/manual/configuration/global.html#horizons

c['caches'] = {             # defaults
    'Changes' : 30000,       # 10 Have seen up to 17K changes be requested in one request.
    'Builds' : 5000,         # 15    
    'chdicts' : 30000,       # 1
    'BuildRequests' : 20,   # 1
    'SourceStamps' : 20,    # 1
    'ssdicts' : 20,         # 20
    'objectids' : 100,       # 1
    'usdicts' : 10,         # 1
}

