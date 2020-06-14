from typing import List

from buildbot.plugins import util

from .build_factory import build_factory, checkout_step, default_step_kwargs
from .steps import GenerateStartMovieCommands, ScummVMTest, download_step

lingo_directory = "./engines/director/lingo/tests/"

lingo_factory = util.BuildFactory()
lingo_factory.addStep(checkout_step)
lingo_factory.addStep(download_step)

lingo_factory.addStep(
    GenerateStartMovieCommands(
        directory=lingo_directory,
        game_id="directortest",
        name="Generate lingo test commands",
        command=["find", lingo_directory, "-name", "*.lingo", "-printf", "%P\n"],
        haltOnFailure=True,
        **default_step_kwargs,
    )
)

name = "All Lingo"
lingo_factory.addStep(
    ScummVMTest(
        name=name,
        description=name,
        descriptionDone=name,
        command=[
            "./scummvm",
            "-c",
            "scummvm.conf",
            "-p",
            lingo_directory,
            "directortest",
        ],
        env={"SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"},
        timeout=5,
        maxTime=10,
        logEnviron=False,
    )
)
