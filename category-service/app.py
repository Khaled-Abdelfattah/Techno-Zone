import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from routes.categories import categories_bp

load_dotenv(".env")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/category_db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")

CORS(app, supports_credentials=True)
db.init_app(app)

app.register_blueprint(categories_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3003)
