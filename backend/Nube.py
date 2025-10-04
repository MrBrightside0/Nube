from flask import Flask


def create_app():
    app = Flask(__name__)

    from api.routes import blueprint

    app.register_blueprint(blueprint)
    return app


app = create_app()


def main():
    app.run(host="0.0.0.0", port=5000)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
