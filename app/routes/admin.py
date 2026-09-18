import os
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, current_app, jsonify, abort)
from flask_login import login_user, logout_user, login_required, current_user
from app.models import (db, User, Property, PropertyImage, PropertyVideo,
                        SiteSettings, ContactMessage)
from app.forms import (LoginForm, PropertyForm, SettingsForm, ChangePasswordForm)
from app.utils import (admin_required, save_image, save_video, delete_file,
                       format_price, get_property_types)

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Bienvenido al panel de administración.', 'success')
            return redirect(next_page or url_for('admin.dashboard'))
        flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('public.index'))


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total = Property.query.count()
    available = Property.query.filter_by(status='disponible').count()
    sold = Property.query.filter_by(status='vendida').count()
    rented = Property.query.filter_by(status='alquilada').count()
    reserved = Property.query.filter_by(status='reservada').count()
    total_views = db.session.query(db.func.sum(Property.views)).scalar() or 0
    top_properties = Property.query.order_by(Property.views.desc()).limit(5).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    unread = ContactMessage.query.filter_by(is_read=False).count()
    
    return render_template('admin/dashboard.html',
                           total=total,
                           available=available,
                           sold=sold,
                           rented=rented,
                           reserved=reserved,
                           total_views=total_views,
                           top_properties=top_properties,
                           recent_messages=recent_messages,
                           unread=unread)


@admin_bp.route('/propiedades')
@login_required
@admin_required
def properties_list():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    q = request.args.get('q', '')
    
    query = Property.query
    if status:
        query = query.filter_by(status=status)
    if q:
        query = query.filter(Property.title.ilike(f'%{q}%'))
    
    pagination = query.order_by(Property.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    
    return render_template('admin/properties.html',
                           properties=pagination.items,
                           pagination=pagination,
                           status=status,
                           q=q)


@admin_bp.route('/propiedades/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def add_property():
    form = PropertyForm()
    if form.validate_on_submit():
        prop = Property(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            currency=form.currency.data,
            transaction_type=form.transaction_type.data,
            property_type=form.property_type.data,
            city=form.city.data,
            location=form.location.data,
            address=form.address.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            bedrooms=form.bedrooms.data or 0,
            bathrooms=form.bathrooms.data or 0,
            area_construction=form.area_construction.data,
            area_land=form.area_land.data,
            features=form.features.data,
            status=form.status.data,
            seo_title=form.seo_title.data or form.title.data,
            seo_description=form.seo_description.data,
            contact_phone=form.contact_phone.data,
            contact_whatsapp=form.contact_whatsapp.data,
            contact_email=form.contact_email.data,
            published=form.published.data
        )
        prop.generate_slug()
        db.session.add(prop)
        db.session.flush()  # Get ID
        
        # Main image
        if form.main_image.data:
            filename = save_image(form.main_image.data)
            if filename:
                prop.main_image = filename
                img = PropertyImage(property_id=prop.id, filename=filename, is_main=True, order=0)
                db.session.add(img)
        
        # Additional images
        if form.images.data:
            order = 1
            for f in form.images.data:
                if f and f.filename:
                    filename = save_image(f)
                    if filename:
                        img = PropertyImage(property_id=prop.id, filename=filename, order=order)
                        db.session.add(img)
                        order += 1
        
        # Videos
        if form.videos.data:
            order = 0
            for f in form.videos.data:
                if f and f.filename:
                    filename = save_video(f)
                    if filename:
                        vid = PropertyVideo(property_id=prop.id, filename=filename, order=order)
                        db.session.add(vid)
                        order += 1
        
        db.session.commit()
        flash(f'Propiedad "{prop.title}" creada correctamente.', 'success')
        return redirect(url_for('admin.properties_list'))
    
    return render_template('admin/property_form.html', form=form, title='Agregar propiedad', is_edit=False)


@admin_bp.route('/propiedades/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_property(id):
    prop = Property.query.get_or_404(id)
    form = PropertyForm(obj=prop)
    
    if form.validate_on_submit():
        prop.title = form.title.data
        prop.description = form.description.data
        prop.price = form.price.data
        prop.currency = form.currency.data
        prop.transaction_type = form.transaction_type.data
        prop.property_type = form.property_type.data
        prop.city = form.city.data
        prop.location = form.location.data
        prop.address = form.address.data
        prop.latitude = form.latitude.data
        prop.longitude = form.longitude.data
        prop.bedrooms = form.bedrooms.data or 0
        prop.bathrooms = form.bathrooms.data or 0
        prop.area_construction = form.area_construction.data
        prop.area_land = form.area_land.data
        prop.features = form.features.data
        prop.status = form.status.data
        prop.seo_title = form.seo_title.data or form.title.data
        prop.seo_description = form.seo_description.data
        prop.contact_phone = form.contact_phone.data
        prop.contact_whatsapp = form.contact_whatsapp.data
        prop.contact_email = form.contact_email.data
        prop.published = form.published.data
        
        # Regenerate slug only if title changed significantly
        if prop.slug != form.title.data.lower().replace(' ', '-'):
            # Keep existing slug for SEO unless user wants change - for simplicity keep it
            pass
        
        # New main image
        if form.main_image.data and form.main_image.data.filename:
            # Remove old main flag
            for img in prop.images:
                img.is_main = False
            filename = save_image(form.main_image.data)
            if filename:
                if prop.main_image:
                    delete_file(prop.main_image)
                prop.main_image = filename
                img = PropertyImage(property_id=prop.id, filename=filename, is_main=True, order=0)
                db.session.add(img)
        
        # Additional images
        if form.images.data:
            max_order = db.session.query(db.func.max(PropertyImage.order)).filter_by(property_id=prop.id).scalar() or 0
            for f in form.images.data:
                if f and f.filename:
                    filename = save_image(f)
                    if filename:
                        max_order += 1
                        img = PropertyImage(property_id=prop.id, filename=filename, order=max_order)
                        db.session.add(img)
        
        # Videos
        if form.videos.data:
            max_order = db.session.query(db.func.max(PropertyVideo.order)).filter_by(property_id=prop.id).scalar() or 0
            for f in form.videos.data:
                if f and f.filename:
                    filename = save_video(f)
                    if filename:
                        max_order += 1
                        vid = PropertyVideo(property_id=prop.id, filename=filename, order=max_order)
                        db.session.add(vid)
        
        db.session.commit()
        flash(f'Propiedad "{prop.title}" actualizada.', 'success')
        return redirect(url_for('admin.edit_property', id=prop.id))
    
    return render_template('admin/property_form.html',
                           form=form, prop=prop, title='Editar propiedad', is_edit=True)


@admin_bp.route('/propiedades/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def delete_property(id):
    prop = Property.query.get_or_404(id)
    title = prop.title
    
    # Delete media files
    for img in prop.images:
        delete_file(img.filename, 'images')
    for vid in prop.videos:
        delete_file(vid.filename, 'videos')
    if prop.main_image:
        delete_file(prop.main_image, 'images')
    
    db.session.delete(prop)
    db.session.commit()
    flash(f'Propiedad "{title}" eliminada.', 'success')
    return redirect(url_for('admin.properties_list'))


@admin_bp.route('/propiedades/<int:prop_id>/imagen/<int:img_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def delete_image(prop_id, img_id):
    img = PropertyImage.query.filter_by(id=img_id, property_id=prop_id).first_or_404()
    prop = Property.query.get_or_404(prop_id)
    
    delete_file(img.filename, 'images')
    if prop.main_image == img.filename:
        prop.main_image = None
        # Set next image as main if available
        next_img = prop.images.filter(PropertyImage.id != img.id).first()
        if next_img:
            next_img.is_main = True
            prop.main_image = next_img.filename
    
    db.session.delete(img)
    db.session.commit()
    flash('Imagen eliminada.', 'success')
    return redirect(url_for('admin.edit_property', id=prop_id))


@admin_bp.route('/propiedades/<int:prop_id>/imagen/<int:img_id>/principal', methods=['POST'])
@login_required
@admin_required
def set_main_image(prop_id, img_id):
    prop = Property.query.get_or_404(prop_id)
    img = PropertyImage.query.filter_by(id=img_id, property_id=prop_id).first_or_404()
    
    for i in prop.images:
        i.is_main = False
    img.is_main = True
    prop.main_image = img.filename
    db.session.commit()
    flash('Imagen principal actualizada.', 'success')
    return redirect(url_for('admin.edit_property', id=prop_id))


@admin_bp.route('/propiedades/<int:prop_id>/video/<int:vid_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def delete_video(prop_id, vid_id):
    vid = PropertyVideo.query.filter_by(id=vid_id, property_id=prop_id).first_or_404()
    delete_file(vid.filename, 'videos')
    db.session.delete(vid)
    db.session.commit()
    flash('Video eliminado.', 'success')
    return redirect(url_for('admin.edit_property', id=prop_id))


@admin_bp.route('/configuracion', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    settings = SiteSettings.get_settings()
    form = SettingsForm(obj=settings)
    
    if form.validate_on_submit():
        settings.company_name = form.company_name.data
        settings.phone = form.phone.data
        settings.whatsapp = form.whatsapp.data
        settings.email = form.email.data
        settings.address = form.address.data
        settings.about_text = form.about_text.data
        settings.facebook = form.facebook.data
        settings.instagram = form.instagram.data
        settings.hero_title = form.hero_title.data
        settings.hero_subtitle = form.hero_subtitle.data
        db.session.commit()
        flash('Configuración guardada.', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', form=form)


@admin_bp.route('/mensajes')
@login_required
@admin_required
def messages():
    page = request.args.get('page', 1, type=int)
    pagination = ContactMessage.query.order_by(ContactMessage.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/messages.html', messages=pagination.items, pagination=pagination)


@admin_bp.route('/mensajes/<int:id>/leer', methods=['POST'])
@login_required
@admin_required
def mark_read(id):
    msg = ContactMessage.query.get_or_404(id)
    msg.is_read = True
    db.session.commit()
    return redirect(url_for('admin.messages'))


@admin_bp.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Contraseña actualizada correctamente.', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Contraseña actual incorrecta.', 'danger')
    return render_template('admin/change_password.html', form=form)
