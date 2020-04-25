from buildbot.plugins import util, steps
from buildbot.process import buildstep, logobserver
from twisted.internet import defer

from buildbot.steps.shell import Test


class GenerateStartMovieCommands(buildstep.ShellMixin, steps.BuildStep):
    """Generate the steps to build all lingo files."""

    def __init__(self, directory=None, target=None, **kwargs):
        if directory is None or target is None:
            raise Exception  # ?? how should a raise be done in Buildbot?
        self.directory = directory
        self.target = target
        kwargs = self.setupShellMixin(kwargs)

        super().__init__(**kwargs)
        self.observer = logobserver.BufferLogObserver()
        self.addLogObserver("stdio", self.observer)

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
                        command=[
                            "./scummvm",
                            "-p",
                            f"{self.directory}",
                            f"--start-movie={name}",
                            f"{self.target}",
                        ],
                        env={"SDL_VIDEODRIVER": "dummy",
                             "SDL_AUDIODRIVER": "dummy"},
                        timeout=5,
                        maxTime=10,
                        logEnviron=False,
                    )
                    for name in scripts
                ]
            )
        return result
