import os.path
from dataclasses import dataclass
from typing import List, Union

from buildbot.config import BuilderConfig
from buildbot.plugins import util

from .build_factory import default_step_kwargs
from .env import env
from .steps import GenerateStartMovieCommands, download_step


@dataclass(frozen=True)
class TestTarget:
    name: str
    directory_var: str
    game_id: str
    platform: str  # mac/win
    debugflags: str = "fewframesonly,fast"

    @property
    def builder_name(self) -> str:
        return f"{self.name}:{self.platform}"

    @property
    def enabled(self) -> bool:
        return bool(self.directory_var)

    @property
    def directory(self) -> str:
        return env[self.directory_var]


available_test_targets: List[TestTarget] = [
    TestTarget("D4dictionary", "D4_TEST_DIR_WIN", "director", "win"),
    TestTarget("D4dictionary", "D4_TEST_DIR_MAC", "director", "mac"),
    TestTarget(
        "Chop Suey",
        "CHOP_SUEY_DIR_WIN",
        "chopsuey",
        "win",
        "fewframesonly,fast,bytecode",
    ),
    TestTarget("Spaceship Warlock", "SPACESHIP_WARLOCK_DIR_WIN", "warlock", "win"),
    TestTarget("Journeyman Project", "JOURNEYMAN_PROJECT_DIR_WIN", "jman", "win"),
]

test_targets: List[TestTarget] = [
    target for target in available_test_targets if target.enabled
]


def generate_builder(target: TestTarget) -> BuilderConfig:
    factory = util.BuildFactory()
    factory.addStep(download_step)
    factory.addStep(
        GenerateStartMovieCommands(
            directory=target.directory,
            game_id=target.game_id,
            debugflags=target.debugflags,
            name=f"Generate commands: {target.name}:{target.platform}",
            command=["cat", os.path.join(target.directory, "test_scripts.txt")],
            haltOnFailure=True,
            **default_step_kwargs,
        )
    )
    return BuilderConfig(
        name=target.builder_name, workernames=["director-worker"], factory=factory
    )
