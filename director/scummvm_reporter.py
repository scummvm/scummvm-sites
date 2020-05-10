from buildbot.process.results import FAILURE, SUCCESS
from buildbot.reporters import utils
from buildbot.reporters.message import MessageFormatter
from buildbot.reporters.notifier import NotifierBase
from buildbot.util import httpclientservice
from buildbot_slack.reporter import SlackStatusPush
from twisted.internet import defer
from twisted.python import log


class WebHookReporter(NotifierBase):
    """
    Reporter for ScummVM Director Discord channel.
    """

    def checkConfig(self, webhook_url: str, **kwargs) -> None:
        super().checkConfig(**kwargs)
        httpclientservice.HTTPClientService.checkAvailable(self.__class__.__name__)

    @defer.inlineCallbacks
    def reconfigService(self, webhook_url: str, **kwargs):
        super().reconfigService(**kwargs)
        self._http = yield httpclientservice.HTTPClientService.getService(
            self.master, webhook_url
        )

    @defer.inlineCallbacks
    def buildMessage(self, name, builds, results):
        """Original buildMessage, except it handles a JSON body."""
        patches = []
        logs = []
        body = ""
        subject = None
        msgtype = None
        users = set()
        for build in builds:
            if self.addPatch:
                ss_list = build["buildset"]["sourcestamps"]

                for ss in ss_list:
                    if "patch" in ss and ss["patch"] is not None:
                        patches.append(ss["patch"])
            if self.addLogs:
                build_logs = yield self.getLogsForBuild(build)
                logs.extend(build_logs)

            if "prev_build" in build and build["prev_build"] is not None:
                previous_results = build["prev_build"]["results"]
            else:
                previous_results = None
            blamelist = yield self.getResponsibleUsersForBuild(
                self.master, build["buildid"]
            )
            buildmsg = yield self.messageFormatter.formatMessageForBuildResults(
                self.mode,
                name,
                build["buildset"],
                build,
                self.master,
                previous_results,
                blamelist,
            )
            users.update(set(blamelist))
            msgtype = buildmsg["type"]
            if "body" in buildmsg:
                body = buildmsg["body"]
            if "subject" in buildmsg:
                subject = buildmsg["subject"]

        yield self.sendMessage(
            body, subject, msgtype, name, results, builds, list(users), patches, logs
        )

    @defer.inlineCallbacks
    def sendMessage(
        self,
        body,
        subject=None,
        type=None,
        builderName=None,
        results=None,
        builds=None,
        users=None,
        patches=None,
        logs=None,
        worker=None,
    ):
        yield self._http.post("", json=body)


class JSONMessageFormatter:
    """
    Formatter that know about JSON.

    This class could and should be simpler, except, it isn't.
    There must be a yield in formatMessageforBuildResults,
    the ctx needs to be queried.

    Otherwise the sending of the build message just wont trigger.
    """

    wantProperties = False
    wantSteps = True
    wantLogs = False
    ctx = {"type": "JSON"}

    def renderMessage(self, ctx: dict) -> dict:

        json = {
            "embeds": [
                {
                    "url": ctx["build_url"],
                    "title": "New Failure/New success",
                    "fields": [{"name": "New failures", "value": "BLALBL, BLA BLA"}],
                }
            ]
        }
        if ctx["build"]["results"] == SUCCESS:

            color = 0x36A64F
            json = {
                "embeds": [
                    {
                        "url": ctx["build_url"],
                        "title": f"Success {ctx['buildername']}",
                        "color": color,
                    }
                ]
            }
        elif ctx["build"]["results"] == FAILURE:
            color = 0xFC0303
            json = {
                "embeds": [
                    {
                        "url": ctx["build_url"],
                        "title": "Failure",
                        "color": color,
                        "fields": [
                            {
                                "name": "broken steps",
                                "value": ctx["build"]["state_string"],
                            }
                        ],
                    }
                ]
            }

        msgdict = {"body": json}
        if "type" in ctx:
            msgdict["type"] = ctx["type"]
        return msgdict

    def buildAdditionalContext(self, master, ctx):
        ctx.update(self.ctx)

    @defer.inlineCallbacks
    def formatMessageForBuildResults(
        self, mode, buildername, buildset, build, master, previous_results, blamelist
    ):
        ctx = dict(
            mode=mode,
            buildername=buildername,
            workername=build["properties"].get("workername", ["<unknown>"])[0],
            buildset=buildset,
            build=build,
            previous_results=previous_results,
            build_url=utils.getURLForBuild(
                master, build["builder"]["builderid"], build["number"]
            ),
            buildbot_url=master.config.buildbotURL,
            blamelist=blamelist,
        )

        yield self.buildAdditionalContext(master, ctx)
        msgdict = self.renderMessage(ctx)
        return msgdict
