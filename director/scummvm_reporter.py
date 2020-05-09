from buildbot.process.results import SUCCESS
from buildbot.reporters import utils
from buildbot_slack.reporter import SlackStatusPush
from twisted.internet import defer


class ScummVMDirectorReporter(SlackStatusPush):
    """
    Reporter for ScummVM Director Discord channel.

    - Always send messages for the builder
    - Only send messages for subbuilders when they fail
    """

    neededDetails = dict(wantProperties=True, wantSteps=True, wantPreviousBuild=True)
    name = "ScummVMDirectorReporter"

    def filterBuilds(self, build: dict, event_name: str) -> bool:
        """
        Filter the builds to reduce spam.

        For build finishes:
            With success: don't show the subbuild.
            On failure: only show the failed subbuild.
        """

        is_subbuild = bool(build["buildset"]["parent_buildid"])
        if event_name == "buildFinished":
            failure = build["results"] != SUCCESS
            return is_subbuild == failure
        return False

    def buildStarted(self, key, build):
        return self.getMoreInfoAndSendScummVM(key, build, "buildStarted")

    def buildFinished(self, key, build):
        return self.getMoreInfoAndSendScummVM(key, build, "buildFinished")

    @defer.inlineCallbacks
    def getMoreInfoAndSendScummVM(self, key, build, event_name):
        yield utils.getDetailsForBuild(self.master, build, **self.neededDetails)
        if self.filterBuilds(build, event_name):
            return self.send(build, key[2])
