from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Property(db.Model):
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    
    # Pricing & type
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    transaction_type = db.Column(db.String(20), nullable=False)  # venta / alquiler
    property_type = db.Column(db.String(50), nullable=False)  # casa, apartamento, solar, etc.
    
    # Location
    city = db.Column(db.String(100), nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Specs
    bedrooms = db.Column(db.Integer, default=0)
    bathrooms = db.Column(db.Integer, default=0)
    area_construction = db.Column(db.Float)  # m² construcción
    area_land = db.Column(db.Float)  # m² terreno
    features = db.Column(db.Text)  # JSON or comma-separated
    
    # Status
    status = db.Column(db.String(20), default='disponible', index=True)  # disponible, vendida, alquilada, reservada
    
    # SEO
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(300))
    
    # Contact (override company defaults if needed)
    contact_phone = db.Column(db.String(50))
    contact_whatsapp = db.Column(db.String(50))
    contact_email = db.Column(db.String(120))
    
    # Stats
    views = db.Column(db.Integer, default=0)
    
    # Media
    main_image = db.Column(db.String(300))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    
    # Relationships
    images = db.relationship('PropertyImage', backref='property', lazy='dynamic',
                             cascade='all, delete-orphan', order_by='PropertyImage.order')
    videos = db.relationship('PropertyVideo', backref='property', lazy='dynamic',
                             cascade='all, delete-orphan', order_by='PropertyVideo.order')
    
    def generate_slug(self):
        base = slugify(self.title)
        slug = base
        counter = 1
        while Property.query.filter_by(slug=slug).first():
            slug = f"{base}-{counter}"
            counter += 1
        self.slug = slug
    
    def get_features_list(self):
        if not self.features:
            return []
        return [f.strip() for f in self.features.split(',') if f.strip()]
    
    def get_status_label(self):
        labels = {
            'disponible': 'Disponible',
            'vendida': 'Vendida',
            'alquilada': 'Alquilada',
            'reservada': 'Reservada'
        }
        return labels.get(self.status, self.status.title())
    
    def get_status_class(self):
        classes = {
            'disponible': 'badge-available',
            'vendida': 'badge-sold',
            'alquilada': 'badge-rented',
            'reservada': 'badge-reserved'
        }
        return classes.get(self.status, 'badge-available')
    
    def get_main_image_url(self):
        if self.main_image:
            return f'/static/uploads/images/{self.main_image}'
        first = self.images.first()
        if first:
            return f'/static/uploads/images/{first.filename}'
        return '/static/css/placeholder.jpg'
    
    def increment_views(self):
        self.views += 1
        db.session.commit()
    
    def __repr__(self):
        return f'<Property {self.title}>'


class PropertyImage(db.Model):
    __tablename__ = 'property_images'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    alt_text = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_url(self):
        return f'/static/uploads/images/{self.filename}'
    
    def __repr__(self):
        return f'<PropertyImage {self.filename}>'


class PropertyVideo(db.Model):
    __tablename__ = 'property_videos'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    title = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_url(self):
        return f'/static/uploads/videos/{self.filename}'
    
    def __repr__(self):
        return f'<PropertyVideo {self.filename}>'


class SiteSettings(db.Model):
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), default='Premium Real Estate')
    phone = db.Column(db.String(50), default='+504 9999-9999')
    whatsapp = db.Column(db.String(50), default='50499999999')
    email = db.Column(db.String(120), default='info@premiumrealestate.com')
    address = db.Column(db.String(300), default='Tegucigalpa, Honduras')
    about_text = db.Column(db.Text)
    facebook = db.Column(db.String(200))
    instagram = db.Column(db.String(200))
    logo = db.Column(db.String(300))
    hero_image = db.Column(db.String(300))
    hero_title = db.Column(db.String(200), default='Encuentra tu propiedad ideal')
    hero_subtitle = db.Column(db.String(300), default='Las mejores casas, apartamentos y terrenos')
    
    @classmethod
    def get_settings(cls):
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    property = db.relationship('Property', backref='messages')
    
    def __repr__(self):
        return f'<ContactMessage from {self.name}>'
