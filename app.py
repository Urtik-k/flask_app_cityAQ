from flask import Flask
from flask_migrate import Migrate
from routes import url_routes
from database import db
from models import Measurement

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'super_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_data.db'

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(url_routes)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", debug=True)