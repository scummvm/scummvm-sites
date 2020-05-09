"""Build Factory to configure, compile and build the scummvm binary."""

import os.path

from buildbot.plugins import steps, util

default_step_kwargs = {"logEnviron": False}

build_factory = util.BuildFactory()
# check out the source
checkout_step = steps.GitHub(
    repourl="git://github.com/scummvm/scummvm.git",
    mode="incremental",
    **default_step_kwargs,
)
build_factory.addStep(checkout_step)
# run the tests (note that this will require that 'trial' is installed)
build_factory.addStep(
    steps.Configure(
        command=["./configure", "--disable-all-engines", "--enable-engine=director",],
        env={"CXX": "ccache g++"},
        **default_step_kwargs,
    )
)
build_factory.addStep(steps.Compile(command=["make"], **default_step_kwargs))


master_dir = os.path.dirname(__file__)
master_file = os.path.join(master_dir, "scummvm-binary")
worker_file = "scummvm"

build_factory.addStep(steps.FileUpload(workersrc=worker_file, masterdest=master_file))

build_factory.addStep(
    steps.Trigger(schedulerNames=["Director Tests"], waitForFinish=True)
)
