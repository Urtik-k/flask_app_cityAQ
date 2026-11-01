import os

from flask import Flask
from flask_migrate import Migrate

from database import db
from models import Measurement  # noqa: F401  (potrzebne dla migracji)
from routes import url_routes

try:
    from dotenv import load_dotenv
    load_dotenv()  # wczytuje OPENAQ_API_KEY z pliku .env, jeśli istnieje
except ImportError:
    pass

migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_data.db'

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(url_routes)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="127.0.0.1", debug=True)
