from router_controller.config import Config


def test_default_application_name():
    assert Config.APP_NAME == "Router Pi Controller"

def test_default_application_user():
    assert Config.APPLICATION_USER == "router-controller"


def test_default_web_port():
    assert Config.PORT == 8080


def test_default_router_port():
    assert Config.ROUTER_SSH_PORT == 22


def test_default_router_user():
    assert Config.ROUTER_SSH_USER == "root"


def test_database_path_is_inside_data_directory():
    assert Config.get_database_path().parent == Config.get_data_dir()
    
def test_default_data_directory():
    assert str(Config.get_data_dir()) == "/var/lib/router-pi-controller"
