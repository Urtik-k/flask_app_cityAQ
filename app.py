from flask import Flask
from routes import url_routes
from database import db
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.data.db'
db.init_app(app)
app.register_blueprint(url_routes)

# with app.app_context():
#     db.create_all()


if __name__ == '__main__':
    app.run(debug=True)