"""
#from openwrt_controller import __version__

#def test_version():
#    assert __version__ == "0.2.0"

from openwrt_controller import __version__

def test_version_is_defined():
    assert __version__

def test_version_has_three_components():
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
"""

from pathlib import Path
import re

from openwrt_controller import __version__


def test_version_is_defined():
    assert __version__


def test_version_has_three_components():
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_debian_changelog_matches_version():
    changelog = Path("debian/changelog").read_text(encoding="utf-8")

    match = re.search(
        r"^openwrt-pi-controller \(([^)]+)\)",
        changelog,
        re.MULTILINE,
    )

    assert match, "Could not find Debian package version in changelog"

    assert match.group(1) == __version__