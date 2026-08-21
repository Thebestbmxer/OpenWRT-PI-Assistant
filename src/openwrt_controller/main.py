#from . import __version__

#def main():
#    print(f"OpenWrt Pi Controller {__version__}")

from .app import create_app

app = create_app()

def main():
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
    )

if __name__ == "__main__":
    main()