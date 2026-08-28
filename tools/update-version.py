#!/usr/bin/env python3

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

INIT_FILE = ROOT / "src" / "openwrt_controller" / "__init__.py"
CHANGELOG = ROOT / "debian" / "changelog"


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


def update_changelog(version: str) -> None:
    text = CHANGELOG.read_text(encoding="utf-8")

    pattern = r"^(openwrt-pi-controller\s+\()[^)]+(\)\s+unstable;\s+urgency=)"

    updated, count = re.subn(
        pattern,
        rf"\g<1>{version}\g<2>",
        text,
        count=1,
        flags=re.MULTILINE,
    )

    if count != 1:
        raise RuntimeError(
            "Could not find the first Debian changelog version entry."
        )

    CHANGELOG.write_text(updated, encoding="utf-8")


def main() -> int:
    version = read_version()

    print(f"Project version: {version}")

    update_changelog(version)

    print(f"Updated Debian changelog to {version}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
