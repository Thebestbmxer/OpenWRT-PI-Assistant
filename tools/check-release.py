#!/usr/bin/env python3

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

INIT_FILE = ROOT / "src" / "router_controller" / "__init__.py"
CHANGELOG = ROOT / "debian" / "changelog"

PACKAGE_NAME = "router-pi-controller"


def read_project_version() -> str:
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

    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise RuntimeError(
            f"Invalid version '{version}'. "
            "Expected MAJOR.MINOR.PATCH."
        )

    return version


def read_debian_version() -> str:
    text = CHANGELOG.read_text(encoding="utf-8")

    match = re.search(
        rf"^{re.escape(PACKAGE_NAME)}\s+\(([^)]+)\)",
        text,
        re.MULTILINE,
    )

    if not match:
        raise RuntimeError(
            f"Could not find {PACKAGE_NAME} version in {CHANGELOG}"
        )

    return match.group(1)


def check_versions(project_version: str, debian_version: str) -> None:
    if project_version != debian_version:
        raise RuntimeError(
            "Version mismatch:\n"
            f"  __init__.py:      {project_version}\n"
            f"  debian/changelog: {debian_version}"
        )


def check_tag(project_version: str, tag: str) -> None:
    expected = f"v{project_version}"

    if tag != expected:
        raise RuntimeError(
            f"Git tag '{tag}' does not match project version "
            f"'{project_version}'. Expected '{expected}'."
        )


def main() -> int:
    try:
        project_version = read_project_version()
        debian_version = read_debian_version()

        check_versions(project_version, debian_version)

        print(f"Project version: {project_version}")
        print(f"Debian version:  {debian_version}")
        print("Version consistency: OK")

        if len(sys.argv) > 1:
            tag = sys.argv[1]
            check_tag(project_version, tag)
            print(f"Git tag:          {tag}")
            print("Git tag consistency: OK")

        print("Release validation passed.")
        return 0

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
