from typing import List, Optional, Any, Dict

from buildbot import config
from buildbot.plugins import steps, util
from buildbot.process import buildstep, logobserver
from buildbot.process.results import FAILURE, worst_status
from twisted.internet import defer

from .build_factory import master_file, worker_file, default_env

download_step = steps.FileDownload(
    mastersrc=master_file, workerdest=worker_file, mode=0o0755,
)


class ScummVMTest(steps.Test):
    """Test steps that treats a specific warning as errors"""

    treat_as_error: str = "######################  LINGO: syntax error"

    def has_error(self, line):
        return self.treat_as_error in line

    def evaluateCommand(self, cmd):
        result = super().evaluateCommand(cmd)
        if any(self.has_error(line) for line in self.loggedWarnings):
            return worst_status(FAILURE, result)
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

    def generate_command(self, name: str) -> List[str]:
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
            self.build.addStepsAfterCurrentStep(
                [
                    ScummVMTest(
                        name=name,
                        description=name,
                        descriptionDone=name,
                        command=self.generate_command(name),
                        env=default_env,
                        timeout=5,
                        maxTime=10,
                        logEnviron=False,
                    )
                    for name in scripts
                ]
            )
        return result
