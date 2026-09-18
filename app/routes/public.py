from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from sqlalchemy import or_, and_
from app.models import db, Property, ContactMessage, SiteSettings
from app.forms import SearchForm, ContactForm
from app.utils import format_price, get_property_types

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    featured = Property.query.filter_by(published=True, status='disponible')\
        .order_by(Property.views.desc()).limit(6).all()
    recent = Property.query.filter_by(published=True)\
        .order_by(Property.created_at.desc()).limit(8).all()
    settings = SiteSettings.get_settings()
    search_form = SearchForm()
    return render_template('index.html',
                           featured=featured,
                           recent=recent,
                           settings=settings,
                           search_form=search_form,
                           property_types=get_property_types())


@public_bp.route('/propiedades')
def properties():
    form = SearchForm(request.args)
    page = request.args.get('page', 1, type=int)
    
    query = Property.query.filter_by(published=True)
    
    # Filters
    if form.q.data:
        q = f"%{form.q.data}%"
        query = query.filter(or_(
            Property.title.ilike(q),
            Property.description.ilike(q),
            Property.location.ilike(q),
            Property.city.ilike(q)
        ))
    
    if form.min_price.data is not None:
        query = query.filter(Property.price >= form.min_price.data)
    if form.max_price.data is not None:
        query = query.filter(Property.price <= form.max_price.data)
    if form.city.data:
        query = query.filter(Property.city.ilike(f"%{form.city.data}%"))
    if form.location.data:
        query = query.filter(Property.location.ilike(f"%{form.location.data}%"))
    if form.property_type.data:
        query = query.filter(Property.property_type == form.property_type.data)
    if form.transaction_type.data:
        query = query.filter(Property.transaction_type == form.transaction_type.data)
    if form.bedrooms.data is not None:
        query = query.filter(Property.bedrooms >= form.bedrooms.data)
    if form.bathrooms.data is not None:
        query = query.filter(Property.bathrooms >= form.bathrooms.data)
    if form.min_area.data is not None:
        query = query.filter(Property.area_construction >= form.min_area.data)
    if form.min_land.data is not None:
        query = query.filter(Property.area_land >= form.min_land.data)
    if form.status.data:
        query = query.filter(Property.status == form.status.data)
    
    # Sorting
    sort = request.args.get('sort', 'newest')
    if sort == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Property.price.desc())
    elif sort == 'popular':
        query = query.order_by(Property.views.desc())
    else:
        query = query.order_by(Property.created_at.desc())
    
    pagination = query.paginate(
        page=page,
        per_page=current_app.config.get('PROPERTIES_PER_PAGE', 12),
        error_out=False
    )
    
    return render_template('properties.html',
                           properties=pagination.items,
                           pagination=pagination,
                           form=form,
                           sort=sort,
                           property_types=get_property_types())


@public_bp.route('/propiedad/<slug>')
def property_detail(slug):
    prop = Property.query.filter_by(slug=slug, published=True).first_or_404()
    prop.increment_views()
    
    related = Property.query.filter(
        Property.property_type == prop.property_type,
        Property.id != prop.id,
        Property.published == True,
        Property.status == 'disponible'
    ).limit(4).all()
    
    contact_form = ContactForm(property_id=prop.id)
    settings = SiteSettings.get_settings()
    
    return render_template('property_detail.html',
                           prop=prop,
                           related=related,
                           contact_form=contact_form,
                           settings=settings,
                           format_price=format_price)


@public_bp.route('/comprar')
def comprar():
    return redirect(url_for('public.properties', transaction_type='venta', status='disponible'))


@public_bp.route('/vender')
def vender():
    settings = SiteSettings.get_settings()
    return render_template('vender.html', settings=settings)


@public_bp.route('/nosotros')
def about():
    settings = SiteSettings.get_settings()
    return render_template('about.html', settings=settings)


@public_bp.route('/contacto', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    settings = SiteSettings.get_settings()
    
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            subject=form.subject.data or 'Consulta general',
            message=form.message.data,
            property_id=form.property_id.data or None
        )
        db.session.add(msg)
        db.session.commit()
        flash('¡Mensaje enviado correctamente! Te contactaremos pronto.', 'success')
        return redirect(url_for('public.contact'))
    
    return render_template('contact.html', form=form, settings=settings)


@public_bp.route('/api/search')
def api_search():
    """Simple API for live search suggestions."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    
    results = Property.query.filter(
        Property.published == True,
        or_(
            Property.title.ilike(f'%{q}%'),
            Property.city.ilike(f'%{q}%'),
            Property.location.ilike(f'%{q}%')
        )
    ).limit(8).all()
    
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'price': p.price,
        'city': p.city,
        'image': p.get_main_image_url()
    } for p in results])
