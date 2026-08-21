__version__ = "0.1.0"
Then create:
src/openwrt_controller/main.py
with:
from . import __version__


def main():
    print(f"OpenWrt Pi Controller {__version__}")


if __name__ == "__main__":
    main()