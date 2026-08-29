from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_upgrade_preserves_persistent_data_path():
    postinst = PROJECT_ROOT / "debian" / "postinst"

    contents = postinst.read_text()

    assert "/var/lib/openwrt-pi-controller" in contents
    assert "chown openwrt-controller:openwrt-controller" in contents

def test_upgrade_script_preserves_data_directory():
    postinst = PROJECT_ROOT / "debian" / "postinst"

    contents = postinst.read_text()

    assert "/var/lib/openwrt-pi-controller" in contents
    assert "chown openwrt-controller:openwrt-controller" in contents

def test_upgrade_preserves_service_account():
    postinst = PROJECT_ROOT / "debian" / "postinst"

    contents = postinst.read_text()

    assert "openwrt-controller" in contents
    assert "--system" in contents
    assert "--shell /usr/sbin/nologin" in contents