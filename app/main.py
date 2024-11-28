from flask import Flask

from app.route.phone_tracker_route import phone_tracker_bp


def run_flask():
    app = Flask(__name__)
    app.register_blueprint(phone_tracker_bp, url_prefix="/api")
    app.run()


if __name__ == '__main__':
    run_flask()
