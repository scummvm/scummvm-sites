"""
Vendorized buildbot.reporter.utils

getPreviousBuild function is altered to look for the latest
master build. It's used by scummvm reporter.
"""

from collections import UserList

from buildbot.process.results import RETRY
from buildbot.reporters.utils import getURLForBuild
from buildbot.util import flatten
from twisted.internet import defer


@defer.inlineCallbacks
def getPreviousBuild(master, build):
    """
    Vendorized getPreviousBuild

    The changes are:
        - a docstring,
        - fetching the buildproperties and
        - check if the branch is master.

    A build is compared to the last build of the master branch.

    The scummvm reporter reports on changed between builds.
    Comparing builds with the latest master makes it easier to
    see changes based on the stable target, i.e. master.
    
    It used to be that PRs could introduce c change that would
    fail on a lot of tests.The next commit on master would show many
    tests as fixed, even though that commit didn't touch them.
    """

    n = build["number"] - 1
    while n >= 0:
        prev = yield master.data.get(("builders", build["builderid"], "builds", n))
        if prev:
            buildproperties = yield master.data.get(
                ("builds", prev["buildid"], "properties"))

            if (prev["results"] != RETRY
                and buildproperties["branch"][0] == "master"
                ):
                return prev
        n -= 1
    return None


@defer.inlineCallbacks
def getDetailsForBuild(master, build, wantProperties=False, wantSteps=False,
                       wantPreviousBuild=False, wantLogs=False):
    """Copied verbatim from buildbot.reporters.utils"""

    buildrequest = yield master.data.get(("buildrequests", build['buildrequestid']))
    buildset = yield master.data.get(("buildsets", buildrequest['buildsetid']))
    build['buildrequest'], build['buildset'] = buildrequest, buildset
    ret = yield getDetailsForBuilds(master, buildset, [build],
                                    wantProperties=wantProperties, wantSteps=wantSteps,
                                    wantPreviousBuild=wantPreviousBuild, wantLogs=wantLogs)
    return ret


@defer.inlineCallbacks
def getDetailsForBuilds(master, buildset, builds, wantProperties=False, wantSteps=False,
                        wantPreviousBuild=False, wantLogs=False):
    """Copied verbatim from buildbot.reporters.utils"""

    builderids = {build['builderid'] for build in builds}

    builders = yield defer.gatherResults([master.data.get(("builders", _id))
                                          for _id in builderids])

    buildersbyid = {builder['builderid']: builder
                    for builder in builders}

    if wantProperties:
        buildproperties = yield defer.gatherResults(
            [master.data.get(("builds", build['buildid'], 'properties'))
             for build in builds])
    else:  # we still need a list for the big zip
        buildproperties = list(range(len(builds)))

    if wantPreviousBuild:
        prev_builds = yield defer.gatherResults(
            [getPreviousBuild(master, build) for build in builds])
    else:  # we still need a list for the big zip
        prev_builds = list(range(len(builds)))

    if wantSteps:
        buildsteps = yield defer.gatherResults(
            [master.data.get(("builds", build['buildid'], 'steps'))
             for build in builds])
        if wantLogs:
            for s in flatten(buildsteps, types=(list, UserList)):
                logs = yield master.data.get(("steps", s['stepid'], 'logs'))
                s['logs'] = list(logs)
                for l in s['logs']:
                    l['content'] = yield master.data.get(("logs", l['logid'], 'contents'))

    else:  # we still need a list for the big zip
        buildsteps = list(range(len(builds)))

    # a big zip to connect everything together
    for build, properties, steps, prev in zip(builds, buildproperties, buildsteps, prev_builds):
        build['builder'] = buildersbyid[build['builderid']]
        build['buildset'] = buildset
        build['url'] = getURLForBuild(
            master, build['builderid'], build['number'])

        if wantProperties:
            build['properties'] = properties

        if wantSteps:
            build['steps'] = list(steps)

        if wantPreviousBuild:
            build['prev_build'] = prev 