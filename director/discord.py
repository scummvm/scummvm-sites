from buildbot.process.results import (
    CANCELLED,
    EXCEPTION,
    FAILURE,
    SUCCESS,
    WARNINGS,
    statusToString,
)
from buildbot.util import httpclientservice, service
from twisted.internet import defer
from twisted.python import log

from .vendor import reporter_utils as utils


def steps_info(build: dict) -> dict[str, int]:
    return {s["name"]: s["results"] for s in build["steps"]}


def isMessageNeededSteps(build: dict, prev_build: dict) -> bool:
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


class DiscordStatusPush(service.BuildbotService):
    """ """

    name = "DiscordStatusPush"

    @defer.inlineCallbacks
    def reconfigService(self, webhookURL, debug=None, **kwargs):
        super().reconfigService(**kwargs)
        self._http = yield httpclientservice.HTTPClientService.getService(
            self.master, webhookURL, debug=debug
        )

        startConsuming = self.master.mq.startConsuming
        self._buildCompleteConsumer = yield startConsuming(
            self.buildComplete, ("builds", None, "finished")
        )

    @defer.inlineCallbacks
    def stopService(self):
        self._buildCompleteConsumer.stopConsuming()

    @defer.inlineCallbacks
    def buildComplete(self, key, build):
        yield self.getBuildDetails(build)

        if self.is_message_needed_by_results(build):
            yield self.build_message(build)
        return

    @defer.inlineCallbacks
    def getBuildDetails(self, build):
        br = yield self.master.data.get(("buildrequests", build["buildrequestid"]))
        buildset = yield self.master.data.get(("buildsets", br["buildsetid"]))
        yield utils.getDetailsForBuilds(
            self.master,
            buildset,
            [build],
            want_properties=True,
            want_steps=True,
            want_previous_build=True,
        )
        prev_steps = yield defer.gatherResults(
            [
                self.master.data.get(("builds", b["buildid"], "steps"))
                for b in [build["prev_build"]]
            ]
        )
        build["prev_build"]["steps"] = prev_steps[0]
        if not self.is_message_needed_by_results(build):
            return None

        report = yield self.build_message(build)
        yield self.sendMessage(report)

    def is_message_needed_by_results(self, build):
        prev = build["prev_build"]
        results = build["results"]

        if results in (EXCEPTION, CANCELLED):
            return False

        return isMessageNeededSteps(build, prev)

    def build_message(self, build):
        current_steps = steps_info(build)
        previous_steps = steps_info(build["prev_build"])

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

        url = utils.getURLForBuild(
            self.master, build["builder"]["builderid"], build["number"]
        )

        buildername = build["properties"]["buildername"][0]
        title = statusToString(build["results"])
        if build["results"] == SUCCESS:
            color = 0x36A64F  # green
            title = f"Success {buildername}"
        elif build["results"] == FAILURE:
            color = 0xFC0303  # red
            title = f"Failure {buildername}"
            if new_successes and not new_failures:
                color = 0x36A64F  # green
                title = f"Improvement {buildername}"
            elif new_successes and new_failures:
                color = 0xE8D44F  # yellow
                title = f"Change {buildername}"

        branch = build["properties"].get("branch", [None])[0]
        if branch.startswith("refs/pull"):
            # A PullRequest branch looks like: refs/pull/3062/head
            PR_number = branch.split("/")[2]
            title = f"PR {PR_number}: {title}"

        fields = []
        if new_failures:
            fields.append(
                {
                    "name": "broken steps",
                    "value": "```diff\n- " + ", ".join(new_failures) + "```",
                }
            )
        if new_successes:
            fields.append(
                {
                    "name": "fixed steps",
                    "value": "```diff\n+ " + ", ".join(new_successes) + "```",
                }
            )

        json = {
            "embeds": [{"url": url, "title": title, "color": color, "fields": fields}]
        }
        return json

    def is_status_2xx(self, code):
        return code // 100 == 2

    @defer.inlineCallbacks
    def sendMessage(self, report):
        response = yield self._http.post("", json=report)
        log.msg(f"{response.code}: ROLAND: message send.")
        if not self.is_status_2xx(response.code):
            log.msg(f"{response.code}: unable to upload status: {response.content}")
