from .app import create_app


app = create_app(
    provision_router=provision_router,
)


def main():
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
    )


if __name__ == "__main__":
    main()

