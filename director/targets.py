import os.path
from dataclasses import dataclass
from enum import Enum
from typing import List, Union

from buildbot.config import BuilderConfig
from buildbot.plugins import util

from .build_factory import default_step_kwargs
from .env import env
from .steps import GenerateStartMovieCommands, download_step


class Platform(Enum):
    WIN: str = "win"
    MAC: str = "mac"


class DirectorVersion(Enum):
    D2: str = "D2"
    D3: str = "D3"
    D4: str = "D4"


WIN = Platform.WIN
MAC = Platform.MAC

D2 = DirectorVersion.D2
D3 = DirectorVersion.D3
D4 = DirectorVersion.D4


@dataclass(frozen=True)
class TestTarget:
    name: str
    directory_var: str
    game_id: str
    platform: Platform
    version: DirectorVersion
    debugflags: str = "fewframesonly,fast"

    @property
    def builder_name(self) -> str:
        return f"{self.name}:{self.platform.value} ({self.version.value})"

    @property
    def enabled(self) -> bool:
        """Target is enabled when the directory is not an empty string."""
        return bool(self.directory)

    @property
    def directory(self) -> str:
        return env[self.directory_var]


available_test_targets: List[TestTarget] = [
    # Name, var name with path to the test directory, scummvm game_id, platform, debugflags
    TestTarget("Spaceship Warlock", "SPACESHIP_WARLOCK_DIR_WIN", "warlock", WIN, D2),
    TestTarget("apartment", "D2_APARTMENT_DIR_MAC", "theapartment", MAC, D2),
    TestTarget("apartment", "D3_APARTMENT_DIR_MAC", "theapartment", MAC, D3),
    TestTarget("apartment", "D4_APARTMENT_DIR_MAC", "theapartment", MAC, D4),
    TestTarget("dictionary", "D4_TEST_DIR_WIN", "director", WIN, D4),
    TestTarget("dictionary", "D4_TEST_DIR_MAC", "director", MAC, D4),
    TestTarget(
        "Mediaband",
        "MEDIABAND_DIR_WIN",
        "mediaband",
        WIN,
        D4,
        "fewframesonly,fast,bytecode",
    ),
    TestTarget(
        "Chop Suey",
        "CHOP_SUEY_DIR_WIN",
        "chopsuey",
        WIN,
        D4,
        "fewframesonly,fast,bytecode",
    ),
    TestTarget("Journeyman Project", "JOURNEYMAN_PROJECT_DIR_WIN", "jman", WIN, D3),
]

test_targets: List[TestTarget] = [
    target for target in available_test_targets if target.enabled
]


def generate_builder(target: TestTarget, workernames: List[str]) -> BuilderConfig:
    factory = util.BuildFactory()
    factory.addStep(download_step)
    factory.addStep(
        GenerateStartMovieCommands(
            directory=target.directory,
            game_id=target.game_id,
            debugflags=target.debugflags,
            name=f"Generate commands: {target.builder_name}",
            command=["cat", os.path.join(target.directory, "test_scripts.txt")],
            haltOnFailure=True,
            **default_step_kwargs,
        )
    )
    return BuilderConfig(
        name=target.builder_name, workernames=workernames, factory=factory
    )
