#!/usr/bin/env python3

from pathlib import Path
import argparse
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INIT_FILE = ROOT / "src" / "router_controller" / "__init__.py"

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def read_version() -> str:
    text = INIT_FILE.read_text(encoding="utf-8")

    match = re.search(
        r'^__version__\s*=\s*["\']([^"\']+)["\']\s*$',
        text,
        re.MULTILINE,
    )

    if not match:
        raise RuntimeError(
            f"Could not find __version__ in {INIT_FILE}"
        )

    version = match.group(1)

    if not VERSION_PATTERN.fullmatch(version):
        raise RuntimeError(
            f"Invalid version '{version}'. "
            "Expected MAJOR.MINOR.PATCH."
        )

    return version


def get_exact_git_tags() -> list[str]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "tag",
            "--points-at",
            "HEAD",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return [
        tag.strip()
        for tag in result.stdout.splitlines()
        if tag.strip()
    ]


def check_git_tag(version: str) -> None:
    expected_tag = f"v{version}"
    tags = get_exact_git_tags()

    if expected_tag not in tags:
        if tags:
            tags_text = ", ".join(tags)
            raise RuntimeError(
                f"Git tag mismatch. Expected exact tag "
                f"'{expected_tag}' at HEAD, but found: {tags_text}"
            )

        raise RuntimeError(
            f"Git tag mismatch. Expected exact tag "
            f"'{expected_tag}' at HEAD, but HEAD is not tagged."
        )

    print(f"Git tag:       {expected_tag}")
    print("Tag check:     PASS")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Router Pi Controller version."
    )
    parser.add_argument(
        "--check-tag",
        action="store_true",
        help="Require the current Git HEAD to have the matching vX.Y.Z tag.",
    )

    args = parser.parse_args()

    try:
        version = read_version()

        print(f"Project version: {version}")

        if args.check_tag:
            check_git_tag(version)

    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("Version check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())