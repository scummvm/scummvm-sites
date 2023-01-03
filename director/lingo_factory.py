from buildbot.plugins import util

from .build_factory import build_factory, checkout_step, default_step_kwargs
from .steps import GenerateStartMovieCommands, download_step

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
