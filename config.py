import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'inmobiliaria-premium-secret-key-change-in-production-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'inmobiliaria.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB max
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi'}
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # App
    PROPERTIES_PER_PAGE = 12
    COMPANY_NAME = os.environ.get('COMPANY_NAME') or 'Premium Real Estate'
    COMPANY_PHONE = os.environ.get('COMPANY_PHONE') or '+504 9999-9999'
    COMPANY_WHATSAPP = os.environ.get('COMPANY_WHATSAPP') or '50499999999'
    COMPANY_EMAIL = os.environ.get('COMPANY_EMAIL') or 'info@premiumrealestate.com'
    COMPANY_ADDRESS = os.environ.get('COMPANY_ADDRESS') or 'Tegucigalpa, Honduras'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
