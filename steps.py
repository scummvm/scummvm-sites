from buildbot.plugins import steps, util
from buildbot.process import buildstep, logobserver
from twisted.internet import defer

from build_factory import master_file, worker_file

download_step = steps.FileDownload(
    mastersrc=master_file, workerdest=worker_file, mode=755,
)


class GenerateStartMovieCommands(buildstep.ShellMixin, steps.BuildStep):
    """Generate the steps to build all lingo files."""

    def __init__(self, directory=None, target=None, debugflags=None, **kwargs):
        if directory is None or target is None:
            raise Exception  # ?? how should a raise be done in Buildbot?
        self.directory = directory
        self.target = target
        self.debugflags = ""
        if debugflags:
            self.debugflags = f"--debugflags={debugflags}"
        kwargs = self.setupShellMixin(kwargs)

        super().__init__(**kwargs)
        self.observer = logobserver.BufferLogObserver()
        self.addLogObserver("stdio", self.observer)

    def generate_command(self, name):
        command = [
            "./scummvm",
            "-p",
            f"{self.directory}",
            f"--start-movie={name}",
            f"{self.target}",
        ]
        if self.debugflags:
            command.append(f"{self.debugflags}")
        return command

    @defer.inlineCallbacks
    def run(self):
        cmd = yield self.makeRemoteShellCommand()
        yield self.runCommand(cmd)

        result = cmd.results()
        if result == util.SUCCESS:
            stdout = self.observer.getStdout()
            scripts = [
                line.split("/")[-1] for line in stdout.split("\n") if line.strip()
            ]
            self.build.addStepsAfterCurrentStep(
                [
                    steps.Test(
                        name=name,
                        description=name,
                        descriptionDone=name,
                        command=self.generate_command(name),
                        env={"SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"},
                        timeout=5,
                        maxTime=10,
                        logEnviron=False,
                    )
                    for name in scripts
                ]
            )
        return result
