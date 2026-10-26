import os
from flask import Flask
from .models import db


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///leads.db")
    app.config["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")
    if config:
        app.config.update(config)
    db.init_app(app)
    from .routes import bp
    app.register_blueprint(bp)
    with app.app_context():
        db.create_all()
    return app
