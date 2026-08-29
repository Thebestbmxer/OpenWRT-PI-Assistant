from pathlib import Path


SERVICE_FILE = (
    Path(__file__).parents[2]
    / "packaging"
    / "systemd"
    / "openwrt-controller.service"
)


def test_systemd_service_exists():
    assert SERVICE_FILE.exists()


def test_systemd_service_contains_required_settings():
    contents = SERVICE_FILE.read_text()

    assert "Description=OpenWrt Pi Controller" in contents
    assert "User=openwrt-controller" in contents
    assert "Group=openwrt-controller" in contents
    assert "ExecStart=/usr/bin/openwrt-controller" in contents
    assert "Restart=on-failure" in contents
    assert "WantedBy=multi-user.target" in contents