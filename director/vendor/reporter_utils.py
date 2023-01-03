"""
Vendorized buildbot.reporter.utils

getPreviousBuild function is altered to look for the latest
master build. It's used by scummvm reporter.
"""

from buildbot.process.results import RETRY
from buildbot.reporters.utils import get_url_for_log
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
                ("builds", prev["buildid"], "properties")
            )

            if prev["results"] != RETRY and buildproperties["branch"][0] == "master":
                return prev
        n -= 1
    return None


@defer.inlineCallbacks
def getDetailsForBuilds(
    master,
    buildset,
    builds,
    want_properties=False,
    want_steps=False,
    want_previous_build=False,
    want_logs=False,
    want_logs_content=False,
):

    builderids = {build["builderid"] for build in builds}

    builders = yield defer.gatherResults(
        [master.data.get(("builders", _id)) for _id in builderids]
    )

    buildersbyid = {builder["builderid"]: builder for builder in builders}

    if want_properties:
        buildproperties = yield defer.gatherResults(
            [
                master.data.get(("builds", build["buildid"], "properties"))
                for build in builds
            ]
        )
    else:  # we still need a list for the big zip
        buildproperties = list(range(len(builds)))

    if want_previous_build:
        prev_builds = yield defer.gatherResults(
            [getPreviousBuild(master, build) for build in builds]
        )
    else:  # we still need a list for the big zip
        prev_builds = list(range(len(builds)))

    if want_logs_content:
        want_logs = True
    if want_logs:
        want_steps = True

    if want_steps:  # pylint: disable=too-many-nested-blocks
        buildsteps = yield defer.gatherResults(
            [master.data.get(("builds", build["buildid"], "steps")) for build in builds]
        )
        if want_logs:
            for build, build_steps in zip(builds, buildsteps):
                for s in build_steps:
                    logs = yield master.data.get(("steps", s["stepid"], "logs"))
                    s["logs"] = list(logs)
                    for l in s["logs"]:
                        l["url"] = get_url_for_log(
                            master,
                            build["builderid"],
                            build["number"],
                            s["number"],
                            l["slug"],
                        )
                        if want_logs_content:
                            l["content"] = yield master.data.get(
                                ("logs", l["logid"], "contents")
                            )

    else:  # we still need a list for the big zip
        buildsteps = list(range(len(builds)))

    # a big zip to connect everything together
    for build, properties, steps, prev in zip(
        builds, buildproperties, buildsteps, prev_builds
    ):
        build["builder"] = buildersbyid[build["builderid"]]
        build["buildset"] = buildset
        build["url"] = getURLForBuild(master, build["builderid"], build["number"])

        if want_properties:
            build["properties"] = properties

        if want_steps:
            build["steps"] = list(steps)

        if want_previous_build:
            build["prev_build"] = prev


def getURLForBuild(master, builderid, build_number):
    prefix = master.config.buildbotURL
    return prefix + f"#/builders/{builderid}/builds/{build_number}"
