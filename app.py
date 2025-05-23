from flask import Flask
from flask_cors import CORS
from config import Config
from models import SessionLocal
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.videos import videos_bp
from blueprints.theme_weeks import theme_weeks_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Разрешить CORS для всех методов и заголовков
    CORS(app)
    
    # Регистрация blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(videos_bp, url_prefix='/api/videos')
    app.register_blueprint(theme_weeks_bp, url_prefix='/api/theme-weeks')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
