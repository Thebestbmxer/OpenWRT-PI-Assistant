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
