"""Screenshot comparison for Director buildbot tests.

Uses comparison logic from imagediff/imagediff.py. Invoked on the worker by
ScreenshotDiffStep after ScummVMTest when screenshot debugflags are enabled.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import urllib.parse
from typing import Callable, Optional

EXIT_OK = 0
EXIT_DIFF = 1
EXIT_NO_BASELINE = 2
EXIT_ERROR = 3

_repo_root = os.path.dirname(os.path.dirname(__file__))
_seen_prefixes_name = ".screenshot_prefixes_seen"


def _load_movie_diff(screenshots_dir: str) -> Callable[..., bool]:
    """Load movie_diff from the vendored imagediff package."""
    os.environ["SCREENSHOTS_DIR"] = screenshots_dir
    imagediff_dir = os.path.join(_repo_root, "imagediff")

    config_spec = importlib.util.spec_from_file_location(
        "imagediff_config", os.path.join(imagediff_dir, "config.py")
    )
    if config_spec is None or config_spec.loader is None:
        raise ImportError("unable to load imagediff config")
    config_module = importlib.util.module_from_spec(config_spec)
    sys.modules["config"] = config_module
    config_spec.loader.exec_module(config_module)

    core_spec = importlib.util.spec_from_file_location(
        "imagediff_core", os.path.join(imagediff_dir, "imagediff.py")
    )
    if core_spec is None or core_spec.loader is None:
        raise ImportError("unable to load imagediff core")
    core_module = importlib.util.module_from_spec(core_spec)
    core_spec.loader.exec_module(core_module)
    return core_module.movie_diff


def list_movie_prefixes(build_path: str) -> list[str]:
    """Return sorted movie filename prefixes in a build directory."""
    prefixes: set[str] = set()
    if not os.path.isdir(build_path):
        return []

    for name in os.listdir(build_path):
        if not name.endswith(".png") or "-" not in name:
            continue
        prefixes.add(name.rsplit("-", 1)[0])

    return sorted(prefixes)


def _seen_prefixes_path(screenshots_dir: str, target: str, build: str) -> str:
    return os.path.join(screenshots_dir, target, build, _seen_prefixes_name)


def _read_seen_prefixes(path: str) -> set[str]:
    if not os.path.isfile(path):
        return set()
    with open(path, encoding="utf-8") as handle:
        return {line.strip() for line in handle if line.strip()}


def _write_seen_prefixes(path: str, prefixes: set[str]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for prefix in sorted(prefixes):
            handle.write(f"{prefix}\n")


def prefixes_for_step(
    screenshots_dir: str,
    target: str,
    build: str,
    *,
    only_new: bool,
) -> list[str]:
    """Return prefixes to compare for this step."""
    build_path = os.path.join(screenshots_dir, target, build)
    current = set(list_movie_prefixes(build_path))
    if not only_new:
        return sorted(current)

    seen_path = _seen_prefixes_path(screenshots_dir, target, build)
    seen = _read_seen_prefixes(seen_path)
    new_prefixes = sorted(current - seen)
    _write_seen_prefixes(seen_path, seen | set(new_prefixes))
    return new_prefixes


def find_baseline_build(
    screenshots_dir: str, target: str, current_build: str
) -> Optional[str]:
    """Return the highest prior build number that has stored screenshots."""
    target_path = os.path.join(screenshots_dir, target)
    if not os.path.isdir(target_path):
        return None

    try:
        current_number = int(current_build)
    except ValueError:
        return None

    candidates: list[int] = []
    for entry in os.listdir(target_path):
        path = os.path.join(target_path, entry)
        if not os.path.isdir(path):
            continue
        try:
            build_number = int(entry)
        except ValueError:
            continue
        if build_number < current_number:
            candidates.append(build_number)

    if not candidates:
        return None

    return str(max(candidates))


def compare_url(
    imagediff_url: str,
    current_build: str,
    baseline_build: str,
    target: str,
    movie_prefix: str,
) -> str:
    """Build an ImageDiff compare URL for a movie prefix."""
    base = imagediff_url.rstrip("/")
    movie = urllib.parse.quote(movie_prefix, safe="")
    return f"{base}/compare/{current_build}/{baseline_build}/{target}/{movie}"


def check_screenshots(
    screenshots_dir: str,
    target: str,
    current_build: str,
    baseline_build: Optional[str] = None,
    movie_prefix: Optional[str] = None,
    *,
    only_new: bool = True,
) -> tuple[int, str]:
    """Compare screenshots and return an exit code plus a human-readable summary."""
    current_path = os.path.join(screenshots_dir, target, current_build)
    if not os.path.isdir(current_path):
        return EXIT_NO_BASELINE, (
            f"No screenshots found for target '{target}' build {current_build} "
            f"under {screenshots_dir}"
        )

    if baseline_build is None:
        baseline_build = find_baseline_build(screenshots_dir, target, current_build)

    if baseline_build is None:
        return EXIT_NO_BASELINE, (
            f"No baseline screenshots for target '{target}' before build {current_build}"
        )

    if movie_prefix:
        prefixes = [movie_prefix]
    elif only_new:
        prefixes = prefixes_for_step(
            screenshots_dir, target, current_build, only_new=True
        )
    else:
        prefixes = list_movie_prefixes(current_path)

    if not prefixes:
        return EXIT_NO_BASELINE, (
            f"No new screenshot frames to compare for target '{target}' "
            f"build {current_build}"
        )

    try:
        movie_diff = _load_movie_diff(screenshots_dir)
    except ImportError as exc:
        return EXIT_ERROR, f"Failed to load imagediff: {exc}"

    diff_prefixes = [
        prefix
        for prefix in prefixes
        if movie_diff(current_build, baseline_build, target, prefix)
    ]

    if not diff_prefixes:
        return EXIT_OK, (
            f"Screenshots match baseline build {baseline_build} "
            f"for target '{target}' build {current_build}"
        )

    lines = [
        "Screenshot differences detected:",
        f"  target: {target}",
        f"  current build: {current_build}",
        f"  baseline build: {baseline_build}",
        "  changed movies:",
    ]
    lines.extend(f"    - {prefix}" for prefix in diff_prefixes)
    return EXIT_DIFF, "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compare Director buildbot screenshots")
    parser.add_argument("--screenshots-dir", default=os.environ.get("SCREENSHOTS_DIR", ""))
    parser.add_argument("--target", required=True, help="ScummVM target name (game_id)")
    parser.add_argument("--build", required=True, help="Current build number")
    parser.add_argument("--baseline", help="Baseline build number (default: previous build)")
    parser.add_argument("--movie-prefix", help="Compare only this ScummVM movie prefix")
    parser.add_argument(
        "--all-prefixes",
        action="store_true",
        help="Compare every prefix in the build directory, not only new ones",
    )
    parser.add_argument("--imagediff-url", default=os.environ.get("IMAGEDIFF_URL", ""))
    args = parser.parse_args(argv)

    if not args.screenshots_dir:
        print("SCREENSHOTS_DIR is not configured", file=sys.stderr)
        return EXIT_ERROR

    exit_code, message = check_screenshots(
        args.screenshots_dir,
        args.target,
        args.build,
        baseline_build=args.baseline,
        movie_prefix=args.movie_prefix,
        only_new=not args.all_prefixes,
    )

    print(message)
    if exit_code == EXIT_DIFF and args.imagediff_url:
        baseline = args.baseline or find_baseline_build(
            args.screenshots_dir, args.target, args.build
        )
        if baseline:
            diff_prefixes = [
                line.removeprefix("    - ")
                for line in message.splitlines()
                if line.startswith("    - ")
            ]
            print("\nCompare in ImageDiff:")
            for prefix in diff_prefixes:
                print(
                    compare_url(
                        args.imagediff_url,
                        args.build,
                        baseline,
                        args.target,
                        prefix,
                    )
                )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
