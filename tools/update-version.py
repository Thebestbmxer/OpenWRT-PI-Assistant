#!/usr/bin/env python3

from pathlib import Path
import re
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

INIT_FILE = ROOT / "src" / "openwrt_controller" / "__init__.py"
CHANGELOG = ROOT / "debian" / "changelog"

PACKAGE_NAME = "openwrt-pi-controller"
DISTRIBUTION = "unstable"
URGENCY = "medium"
MAINTAINER = "OpenWrt Pi Controller Project <maintainer@example.invalid>"


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

    return match.group(1)


def get_existing_version() -> str:
    text = CHANGELOG.read_text(encoding="utf-8")

    match = re.search(
        rf"^{re.escape(PACKAGE_NAME)}\s+\(([^)]+)\)\s+"
        rf"{re.escape(DISTRIBUTION)};\s+urgency=",
        text,
        re.MULTILINE,
    )

    if not match:
        raise RuntimeError(
            f"Could not find an existing {PACKAGE_NAME} changelog entry."
        )

    return match.group(1)


def update_changelog(version: str) -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    existing_version = get_existing_version()

    if existing_version == version:
        print(
            f"Debian changelog already uses version {version}; "
            "no change required."
        )
        return

    date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    new_entry = (
        f"{PACKAGE_NAME} ({version}) {DISTRIBUTION}; "
        f"urgency={URGENCY}\n"
        "\n"
        "  * Update project version.\n"
        "\n"
        f" -- {MAINTAINER}  {date}\n"
        "\n"
    )

    CHANGELOG.write_text(new_entry + text, encoding="utf-8")

    print(
        f"Added Debian changelog entry for {version} "
        f"(previous version: {existing_version})."
    )


def main() -> int:
    version = read_version()

    print(f"Project version: {version}")

    update_changelog(version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
