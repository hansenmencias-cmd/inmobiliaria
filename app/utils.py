import os
import uuid
from functools import wraps
from flask import current_app, flash, redirect, url_for, abort
from flask_login import current_user
from PIL import Image
from werkzeug.utils import secure_filename


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso denegado. Debes iniciar sesión como administrador.', 'danger')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_unique_filename(original_filename):
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    return f"{uuid.uuid4().hex}.{ext}"


def save_image(file, folder='images', max_size=(1920, 1080), quality=85, create_thumb=True):
    """Save and optimize an uploaded image. Returns filename."""
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename, current_app.config['ALLOWED_IMAGE_EXTENSIONS']):
        return None
    
    filename = generate_unique_filename(secure_filename(file.filename))
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)
    filepath = os.path.join(upload_path, filename)
    
    try:
        img = Image.open(file.stream)
        
        # Convert to RGB if necessary (for PNG with transparency, etc.)
        if img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(filepath, 'JPEG', quality=quality, optimize=True)
        
        # Create thumbnail
        if create_thumb:
            thumb_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'thumbs')
            os.makedirs(thumb_path, exist_ok=True)
            thumb = img.copy()
            thumb.thumbnail((400, 300), Image.Resampling.LANCZOS)
            thumb.save(os.path.join(thumb_path, filename), 'JPEG', quality=80, optimize=True)
        
        return filename
    except Exception as e:
        current_app.logger.error(f"Error saving image: {e}")
        return None


def save_video(file, folder='videos'):
    """Save an uploaded video. Returns filename."""
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename, current_app.config['ALLOWED_VIDEO_EXTENSIONS']):
        return None
    
    filename = generate_unique_filename(secure_filename(file.filename))
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)
    filepath = os.path.join(upload_path, filename)
    
    try:
        file.save(filepath)
        return filename
    except Exception as e:
        current_app.logger.error(f"Error saving video: {e}")
        return None


def delete_file(filename, folder='images'):
    """Delete a file from uploads."""
    if not filename:
        return
    try:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, filename)
        if os.path.exists(path):
            os.remove(path)
        # Also remove thumbnail if image
        if folder == 'images':
            thumb = os.path.join(current_app.config['UPLOAD_FOLDER'], 'thumbs', filename)
            if os.path.exists(thumb):
                os.remove(thumb)
    except Exception as e:
        current_app.logger.error(f"Error deleting file: {e}")


def format_price(price, currency='USD'):
    """Format price for display."""
    if currency == 'HNL':
        return f"L {price:,.0f}"
    elif currency == 'EUR':
        return f"€{price:,.0f}"
    return f"${price:,.0f}"


def get_property_types():
    return {
        'casa': 'Casa',
        'apartamento': 'Apartamento',
        'solar': 'Solar / Terreno',
        'local': 'Local Comercial',
        'finca': 'Finca',
        'oficina': 'Oficina',
        'bodega': 'Bodega',
        'otro': 'Otro'
    }
