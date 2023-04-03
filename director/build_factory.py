"""Build Factory to configure, compile and build the scummvm binary."""

import os.path
from typing import Any

from buildbot.plugins import steps, util
from buildbot.process.properties import Property

from .env import settings

default_step_kwargs: dict[str, Any] = {"logEnviron": False}

default_env: dict[str, str] = {
    "SDL_VIDEODRIVER": "dummy",
    "SDL_AUDIODRIVER": "dummy",
    "ASAN_OPTIONS": "detect_leaks=1:abort_on_error=1:disable_coredump=0:unmap_shadow_on_exit=1",
    "BUILD_NUMBER": str(Property("buildnumber")),
}


@util.renderer
def makeCommand(props):
    cpus = int(props.getProperty("nproc")) + 1
    if not cpus:
        cpus = 2
    return ["make", "-j", str(cpus)]


def configure_has_not_been_run(step):
    return not step.getProperty("configure_has_ran")


build_factory = util.BuildFactory()
# check out the source
# TODO: replace with env variable
checkout_step = steps.GitHub(
    repourl=settings["REPOSITORY"],
    mode="incremental",
    **default_step_kwargs,
)
build_factory.addStep(checkout_step)

build_factory.addStep(
    steps.SetPropertyFromCommand(
        name="nproc",
        description="Finding the number of CPUs",
        command="nproc",
        property="nproc",
        **default_step_kwargs,
    )
)

build_factory.addStep(
    # Check for config.mk, which is created when configure runs
    steps.SetPropertyFromCommand(
        name="configure?",
        description="Find if configure has run before",
        command="[ -f config.mk ] && ls -1 config.mk || exit 0",
        property="configure_has_ran",
        **default_step_kwargs,
    )
)

build_factory.addStep(
    steps.Configure(
        command=[
            "./configure",
            "--disable-detection-full",
            "--disable-all-engines",
            "--enable-engine=director",
            "--enable-asan",
            "--enable-lld",
        ],
        env={"CXX": "ccache g++"},
        doStepIf=configure_has_not_been_run,
        **default_step_kwargs,
    )
)


build_factory.addStep(steps.Compile(command=makeCommand, **default_step_kwargs))

master_dir = os.path.dirname(os.path.dirname(__file__))
master_file = os.path.join(master_dir, "scummvm-binary")
worker_file = "scummvm"

build_factory.addStep(steps.FileUpload(workersrc=worker_file, masterdest=master_file))

build_factory.addStep(
    steps.Trigger(schedulerNames=["Director Tests"], waitForFinish=True)
)
