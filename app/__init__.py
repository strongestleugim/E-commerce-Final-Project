from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, request, url_for

from . import models
from .auth_utils import build_next_path
from .blueprints import BLUEPRINTS
from .cli import register_commands
from .config import Config
from .extensions import db, login_manager
from .models import User


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["PRODUCT_IMAGE_UPLOAD_DIR"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    @login_manager.unauthorized_handler
    def handle_unauthorized():
        flash("Please log in to continue.", "error")
        return redirect(url_for("auth.login", next=build_next_path(request)))

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    register_commands(app)

    @app.context_processor
    def inject_layout_globals():
        return {
            "brand_name": app.config["BRAND_NAME"],
            "brand_tagline": app.config["BRAND_TAGLINE"],
            "brand_contact": app.config["BRAND_CONTACT"],
            "preferred_categories": app.config["PREFERRED_CATEGORIES"],
            "demo_disclaimer": app.config["DEMO_DISCLAIMER"],
            "current_year": datetime.now().year,
        }

    return app
