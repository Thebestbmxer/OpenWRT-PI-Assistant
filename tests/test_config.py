from openwrt_controller.config import Config


def test_default_application_name():
    assert Config.APP_NAME == "OpenWrt Pi Controller"


def test_default_web_port():
    assert Config.PORT == 8080


def test_default_openwrt_port():
    assert Config.OPENWRT_SSH_PORT == 22


def test_default_openwrt_user():
    assert Config.OPENWRT_SSH_USER == "root"


def test_database_path_is_inside_data_directory():
    assert Config.DATABASE_PATH.parent == Config.DATA_DIR