from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    login_manager.init_app(app)

    # Importar y registrar blueprints
    from app.routes import routes
    from app.auth import auth
    app.register_blueprint(routes)
    app.register_blueprint(auth)

    return app

app = create_app()