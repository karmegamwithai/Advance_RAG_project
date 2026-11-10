from flask import Flask, jsonify, render_template
from config import Config
from services.mongodb_service import init_mongo
from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.chat import chat_bp
from routes.settings import settings_bp
from pathlib import Path

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    init_mongo(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")

    @app.get("/")
    def health():
        return render_template("index.html")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])
