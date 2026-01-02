# app.py
import os
from flask import Flask
from config import Config
from extensions import db, migrate, login_manager
from blueprints.public import bp as public_bp
from blueprints.shop import bp as shop_bp
from blueprints.admin import bp as admin_bp

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(public_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(admin_bp)

    @app.route("/health")
    def health():
        return "OK", 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)