import re
from typing import Any, Optional

from buildbot import config
from buildbot.plugins import steps, util
from buildbot.process import buildstep, logobserver
from buildbot.process.properties import Property
from buildbot.process.results import FAILURE, worst_status
from twisted.internet import defer

from .build_factory import default_env, master_file, worker_file
from .env import settings

download_step = steps.FileDownload(
    mastersrc=master_file,
    workerdest=worker_file,
    mode=0o0755,
    blocksize=512*1024
)


class ScummVMTest(steps.WarningCountingShellCommand):
    renderables = [
        "suppressionFile",
        "suppressionList",
        "errorPattern",
        "warningPattern",
        "directoryEnterPattern",
        "directoryLeavePattern",
        "maxWarnCount",
    ]

    errorCount = 0
    errorPattern = (
        "^WARNING: ######################  LINGO: syntax error.*|^WARNING: BUILDBOT:.*"
    )

    def __init__(self, errorPattern=None, **kwargs):
        if errorPattern:
            self.errorPattern = errorPattern
        super().__init__(**kwargs)
        self.addLogObserver(
            "stdio", logobserver.LineConsumerLogObserver(self.errorLogConsumer)
        )

    def errorLogConsumer(self):
        ere = self.errorPattern
        if isinstance(ere, str):
            ere = re.compile(ere)

        directoryEnterRe = self.directoryEnterPattern
        if directoryEnterRe is not None and isinstance(directoryEnterRe, str):
            directoryEnterRe = re.compile(directoryEnterRe)

        directoryLeaveRe = self.directoryLeavePattern
        if directoryLeaveRe is not None and isinstance(directoryLeaveRe, str):
            directoryLeaveRe = re.compile(directoryLeaveRe)

        # Check if each line in the output from this command matched our
        # warnings regular expressions. If did, bump the warnings count and
        # add the line to the collection of lines with warnings
        self.loggedErrors = []
        while True:
            _, line = yield
            if directoryEnterRe:
                match = directoryEnterRe.search(line)
                if match:
                    self.directoryStack.append(match.group(1))
                    continue
            if (
                directoryLeaveRe
                and self.directoryStack
                and directoryLeaveRe.search(line)
            ):
                self.directoryStack.pop()
                continue

            match = ere.match(line)
            if match:
                self.loggedErrors.append(line)
                self.errorCount += 1

    @defer.inlineCallbacks
    def createSummary(self):
        super().createSummary()
        if self.errorCount:
            yield self.addCompleteLog(
                f"errors ({self.errorCount})", "\n".join(self.loggedErrors) + "\n"
            )

        errors_stat = self.getStatistic("errors", 0)
        self.setStatistic("errors", errors_stat + self.errorCount)

        old_count = self.getProperty("errors-count", 0)
        self.setProperty(
            "errors-count", old_count + self.warnCount, "ScummVMShellCommand"
        )

    def evaluateCommand(self, cmd):
        result = super().evaluateCommand(cmd)
        if self.errorCount:
            result = worst_status(result, FAILURE)
        return result


class GenerateStartMovieCommands(buildstep.ShellMixin, steps.BuildStep):
    """Generate the steps to build all lingo files."""

    def __init__(
        self,
        directory: str,
        game_id: str,
        debugflags: Optional[str] = None,
        **kwargs: Any,
    ):
        if not directory:
            config.error("directory must be a string")
        if not game_id:
            config.error("game_id must be a string")
        self.directory = directory
        self.game_id = game_id
        self.debugflags = ""
        if debugflags:
            self.debugflags = f"--debugflags={debugflags}"
        kwargs = self.setupShellMixin(kwargs)

        super().__init__(**kwargs)
        self.observer = logobserver.BufferLogObserver()
        self.addLogObserver("stdio", self.observer)

    def generate_command(self, name: str) -> list[str]:
        command = [
            "./scummvm",
            "-c",
            "scummvm.conf",
            "-p",
            self.directory,
            f"--start-movie={name}",
        ]
        if self.debugflags:
            command.append(self.debugflags)
        command.append(self.game_id)
        return command

    @defer.inlineCallbacks
    def run(self):
        cmd = yield self.makeRemoteShellCommand()
        yield self.runCommand(cmd)

        result = cmd.results()
        if result == util.SUCCESS:
            stdout = self.observer.getStdout()
            scripts = sorted(line for line in stdout.split("\n") if line.strip())
            default_env["BUILD_NUMBER"] = Property("buildnumber").__str__()

            self.build.addStepsAfterCurrentStep(
                [
                    ScummVMTest(
                        name=name,
                        description=name,
                        descriptionDone=name,
                        command=self.generate_command(name),
                        env=default_env,
                        timeout=int(settings["TIMEOUT"]),
                        maxTime=int(settings["MAX_TIME"]),
                        interruptSignal="QUIT",
                        logEnviron=False,
                    )
                    for name in scripts
                ]
            )
        return result
