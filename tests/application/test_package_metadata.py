from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def test_postinst_creates_router_controller_service_account():
    postinst = PROJECT_ROOT / "debian" / "postinst"

    contents = postinst.read_text()

    assert "router-controller" in contents
    assert "--system" in contents
    assert "--shell /usr/sbin/nologin" in contents
    assert "--home /var/lib/router-pi-controller" in contents