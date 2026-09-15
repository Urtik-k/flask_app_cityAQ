from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from routes import url_routes
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.data.db'
db = SQLAlchemy(app)
app.register_blueprint(url_routes)


if __name__ == '__main__':
    app.run(debug=True)