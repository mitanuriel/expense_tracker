import os

from .app import create_app


def main():
    app = create_app()
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")


if __name__ == "__main__":
    main()
