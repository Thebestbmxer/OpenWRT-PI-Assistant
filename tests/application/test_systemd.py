from pathlib import Path


SERVICE_FILE = (
    Path(__file__).parents[2]
    / "packaging"
    / "systemd"
    / "router-controller.service"
)


def test_systemd_service_exists():
    assert SERVICE_FILE.exists()


def test_systemd_service_contains_required_settings():
    contents = SERVICE_FILE.read_text()

    assert "Description=Router Pi Controller" in contents
    
    assert "After=network-online.target" in contents
    assert "Wants=network-online.target" in contents

    assert "User=router-controller" in contents
    assert "Group=router-controller" in contents

    assert "ExecStart=/usr/bin/router-controller" in contents

    assert "Restart=always" in contents
    assert "RestartSec=5" in contents

    assert "WantedBy=multi-user.target" in contents
