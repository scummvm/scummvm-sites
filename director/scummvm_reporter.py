from typing import Dict

from buildbot.process.results import CANCELLED, EXCEPTION, FAILURE, SUCCESS, WARNINGS
from buildbot.reporters import utils
from buildbot.reporters.message import MessageFormatter
from buildbot.reporters.notifier import NotifierBase
from buildbot.util import httpclientservice
from buildbot_slack.reporter import SlackStatusPush
from twisted.internet import defer
from twisted.python import log


def steps_info(build: dict) -> Dict[str, int]:
    return {s["name"]: s["results"] for s in build["steps"]}


def isMessageNeeededSteps(build: dict, prev_build: dict) -> bool:
    """
    True when a step result has changed between builds

    Doesn't handle:
        - added steps
        - removed steps
    """
    build_s = steps_info(build).items()
    prev_s = steps_info(prev_build)
    for name, results in build_s:
        if name in prev_s:
            if results != prev_s[name]:
                return True
    return False


class WebHookReporter(NotifierBase):
    """
    Reporter for ScummVM Director Discord channel.
    """

    possible_modes = (
        "change",
        "changesteps",
        "failing",
        "passing",
        "problem",
        "warnings",
        "exception",
        "cancelled",
    )

    def checkConfig(self, webhook_url: str, **kwargs) -> None:
        super().checkConfig(**kwargs)
        httpclientservice.HTTPClientService.checkAvailable(self.__class__.__name__)

    @defer.inlineCallbacks
    def reconfigService(self, webhook_url: str, **kwargs):
        super().reconfigService(**kwargs)
        self._http = yield httpclientservice.HTTPClientService.getService(
            self.master, webhook_url
        )

    def wantPreviousBuild(self):
        for state in ["change", "changesteps", "problem"]:
            if state in self.mode:
                return True
        return False

    @defer.inlineCallbacks
    def buildComplete(self, key, build):
        if self.buildSetSummary:
            return
        br = yield self.master.data.get(("buildrequests", build["buildrequestid"]))
        buildset = yield self.master.data.get(("buildsets", br["buildsetid"]))
        yield utils.getDetailsForBuilds(
            self.master,
            buildset,
            [build],
            wantProperties=self.messageFormatter.wantProperties,
            wantSteps=self.messageFormatter.wantSteps,
            wantPreviousBuild=self.wantPreviousBuild(),
            wantLogs=self.messageFormatter.wantLogs,
        )

        if "changesteps" in self.mode:
            yield utils.getDetailsForBuild(
                self.master, build["prev_build"], wantProperties=True, wantSteps=True
            )
        # only include builds for which isMessageNeeded returns true
        if self.isMessageNeeded(build):
            self.buildMessage(build["builder"]["name"], [build], build["results"])

    def isMessageNeeded(self, build):
        # here is where we actually do something.
        builder = build["builder"]
        scheduler = build["properties"].get("scheduler", [None])[0]
        branch = build["properties"].get("branch", [None])[0]
        results = build["results"]
        if self.builders is not None and builder["name"] not in self.builders:
            return False  # ignore this build
        if self.schedulers is not None and scheduler not in self.schedulers:
            return False  # ignore this build
        if self.branches is not None and branch not in self.branches:
            return False  # ignore this build
        if self.tags is not None and not self.matchesAnyTag(builder["tags"]):
            return False  # ignore this build

        if "changesteps" in self.mode:
            prev = build["prev_build"]
            if isMessageNeeededSteps(build, prev) and results not in (
                EXCEPTION,
                CANCELLED,
            ):
                return True
        if "change" in self.mode:
            prev = build["prev_build"]
            if prev and prev["results"] != results:
                return True
        if "failing" in self.mode and results == FAILURE:
            return True
        if "passing" in self.mode and results == SUCCESS:
            return True
        if "problem" in self.mode and results == FAILURE:
            prev = build["prev_build"]
            if prev and prev["results"] != FAILURE:
                return True
        if "warnings" in self.mode and results == WARNINGS:
            return True
        if "exception" in self.mode and results == EXCEPTION:
            return True
        if "cancelled" in self.mode and results == CANCELLED:
            return True

        return False

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
                previous_build = build["prev_build"]
            else:
                previous_build = None
            blamelist = yield self.getResponsibleUsersForBuild(
                self.master, build["buildid"]
            )
            buildmsg = yield self.messageFormatter.formatMessageForBuildResults(
                self.mode,
                name,
                build["buildset"],
                build,
                self.master,
                previous_build,
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
        current_steps = steps_info(ctx["build"])
        previous_steps = steps_info(ctx["previous_build"])

        new_failures = []
        new_successes = []
        for name, results in current_steps.items():
            if name in previous_steps:
                if results == previous_steps[name]:
                    # result is the same, do nothing
                    continue
                if results in (WARNINGS, SUCCESS):
                    new_successes.append(name)
                if results == FAILURE:
                    new_failures.append(name)

        url = ctx["build_url"]

        if ctx["build"]["results"] == SUCCESS:
            color = 0x36A64F  # green
            title = f"Success {ctx['buildername']}"
        elif ctx["build"]["results"] == FAILURE:
            color = 0xFC0303  # red
            title = f"Failure {ctx['buildername']}"
            if new_successes and not new_failures:
                color = 0x36A64F  # green
                title = f"Improvement {ctx['buildername']}"
            elif new_successes and new_failures:
                color = 0xE8D44F  # yellow
                title = f"Change {ctx['buildername']}"

        fields = []
        if new_failures:
            fields.append(
                {
                    "name": "broken steps",
                    "value": "```diff\n-" + ", ".join(new_failures) + "```",
                }
            )
        if new_successes:
            fields.append(
                {
                    "name": "fixed steps",
                    "value": "```diff\n+" + ", ".join(new_successes) + "```",
                }
            )

        json = {
            "embeds": [{"url": url, "title": title, "color": color, "fields": fields}]
        }

        msgdict = {"body": json}
        if "type" in ctx:
            msgdict["type"] = ctx["type"]
        return msgdict

    def buildAdditionalContext(self, master, ctx):
        ctx.update(self.ctx)

    @defer.inlineCallbacks
    def formatMessageForBuildResults(
        self, mode, buildername, buildset, build, master, previous_build, blamelist
    ):
        ctx = dict(
            mode=mode,
            buildername=buildername,
            workername=build["properties"].get("workername", ["<unknown>"])[0],
            buildset=buildset,
            build=build,
            previous_build=previous_build,
            build_url=utils.getURLForBuild(
                master, build["builder"]["builderid"], build["number"]
            ),
            buildbot_url=master.config.buildbotURL,
            blamelist=blamelist,
        )

        yield self.buildAdditionalContext(master, ctx)
        msgdict = self.renderMessage(ctx)
        return msgdict
