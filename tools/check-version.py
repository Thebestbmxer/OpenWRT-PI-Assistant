#!/usr/bin/env python3

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INIT_FILE = ROOT / "src" / "openwrt_controller" / "__init__.py"


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

    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise RuntimeError(
            f"Invalid version '{version}'. "
            "Expected MAJOR.MINOR.PATCH."
        )

    return version


def main() -> int:
    version = read_version()
    print(f"Project version: {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())