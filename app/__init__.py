import os
from flask import Flask
from flask_login import LoginManager
from config import config
from app.models import db, User, SiteSettings


login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Por favor inicia sesión para acceder al panel.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Ensure upload folders exist
    for folder in ['images', 'videos', 'thumbs']:
        path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(path, exist_ok=True)
    
    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Context processors
    @app.context_processor
    def inject_globals():
        settings = SiteSettings.get_settings()
        return {
            'site_settings': settings,
            'company_name': settings.company_name,
            'whatsapp_number': settings.whatsapp
        }
    
    # Create tables and default admin
    with app.app_context():
        db.create_all()
        # Create default admin if none exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@premiumrealestate.com', is_admin=True)
            admin.set_password('admin123')  # CHANGE THIS IN PRODUCTION!
            db.session.add(admin)
            db.session.commit()
            print('>>> Usuario admin creado: admin / admin123')
        
        # Ensure settings exist
        SiteSettings.get_settings()
    
    return app
