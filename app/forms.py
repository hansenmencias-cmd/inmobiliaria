from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import (
    StringField, TextAreaField, FloatField, IntegerField, SelectField,
    PasswordField, BooleanField, SubmitField, HiddenField
)
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar sesión')


class PropertyForm(FlaskForm):
    title = StringField('Título de la propiedad', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Descripción completa', validators=[DataRequired()])
    price = FloatField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    currency = SelectField('Moneda', choices=[('USD', 'USD'), ('HNL', 'Lempiras'), ('EUR', 'EUR')], default='USD')
    transaction_type = SelectField('Tipo de transacción', choices=[
        ('venta', 'Venta'),
        ('alquiler', 'Alquiler')
    ], validators=[DataRequired()])
    property_type = SelectField('Tipo de propiedad', choices=[
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('solar', 'Solar / Terreno'),
        ('local', 'Local Comercial'),
        ('finca', 'Finca'),
        ('oficina', 'Oficina'),
        ('bodega', 'Bodega'),
        ('otro', 'Otro')
    ], validators=[DataRequired()])
    city = StringField('Ciudad', validators=[DataRequired(), Length(max=100)])
    location = StringField('Ubicación / Zona', validators=[DataRequired(), Length(max=200)])
    address = StringField('Dirección completa', validators=[Optional(), Length(max=300)])
    latitude = FloatField('Latitud (mapa)', validators=[Optional()])
    longitude = FloatField('Longitud (mapa)', validators=[Optional()])
    bedrooms = IntegerField('Habitaciones', validators=[Optional(), NumberRange(min=0)], default=0)
    bathrooms = IntegerField('Baños', validators=[Optional(), NumberRange(min=0)], default=0)
    area_construction = FloatField('m² de construcción', validators=[Optional(), NumberRange(min=0)])
    area_land = FloatField('m² de terreno', validators=[Optional(), NumberRange(min=0)])
    features = TextAreaField('Características (separadas por comas)', validators=[Optional()],
                             render_kw={"placeholder": "Piscina, Jardín, Garaje, Seguridad 24h, ..."})
    status = SelectField('Estado', choices=[
        ('disponible', 'Disponible'),
        ('vendida', 'Vendida'),
        ('alquilada', 'Alquilada'),
        ('reservada', 'Reservada')
    ], default='disponible')
    seo_title = StringField('Título SEO', validators=[Optional(), Length(max=200)])
    seo_description = StringField('Descripción SEO', validators=[Optional(), Length(max=300)])
    contact_phone = StringField('Teléfono de contacto', validators=[Optional(), Length(max=50)])
    contact_whatsapp = StringField('WhatsApp', validators=[Optional(), Length(max=50)])
    contact_email = StringField('Email de contacto', validators=[Optional(), Email(), Length(max=120)])
    published = BooleanField('Publicada', default=True)
    
    # Media
    main_image = FileField('Fotografía principal', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo imágenes')
    ])
    images = MultipleFileField('Fotografías adicionales', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo imágenes')
    ])
    videos = MultipleFileField('Videos', validators=[
        FileAllowed(['mp4', 'webm', 'mov', 'avi'], 'Solo videos')
    ])
    
    submit = SubmitField('Guardar propiedad')


class SearchForm(FlaskForm):
    q = StringField('Buscar', validators=[Optional()])
    min_price = FloatField('Precio mínimo', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Precio máximo', validators=[Optional(), NumberRange(min=0)])
    city = StringField('Ciudad', validators=[Optional()])
    location = StringField('Ubicación', validators=[Optional()])
    property_type = SelectField('Tipo', choices=[
        ('', 'Todos los tipos'),
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('solar', 'Solar / Terreno'),
        ('local', 'Local Comercial'),
        ('finca', 'Finca'),
        ('oficina', 'Oficina'),
        ('bodega', 'Bodega'),
        ('otro', 'Otro')
    ], default='')
    transaction_type = SelectField('Transacción', choices=[
        ('', 'Venta y Alquiler'),
        ('venta', 'Venta'),
        ('alquiler', 'Alquiler')
    ], default='')
    bedrooms = IntegerField('Habitaciones mín.', validators=[Optional(), NumberRange(min=0)])
    bathrooms = IntegerField('Baños mín.', validators=[Optional(), NumberRange(min=0)])
    min_area = FloatField('m² construcción mín.', validators=[Optional()])
    min_land = FloatField('m² terreno mín.', validators=[Optional()])
    status = SelectField('Estado', choices=[
        ('', 'Todos'),
        ('disponible', 'Disponible'),
        ('vendida', 'Vendida'),
        ('alquilada', 'Alquilada'),
        ('reservada', 'Reservada')
    ], default='disponible')
    submit = SubmitField('Buscar')


class ContactForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Teléfono', validators=[Optional(), Length(max=50)])
    subject = StringField('Asunto', validators=[Optional(), Length(max=200)])
    message = TextAreaField('Mensaje', validators=[DataRequired(), Length(min=10)])
    property_id = HiddenField()
    submit = SubmitField('Enviar mensaje')


class SettingsForm(FlaskForm):
    company_name = StringField('Nombre de la empresa', validators=[DataRequired(), Length(max=150)])
    phone = StringField('Teléfono', validators=[DataRequired(), Length(max=50)])
    whatsapp = StringField('WhatsApp (solo números, ej: 50499999999)', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Dirección', validators=[Optional(), Length(max=300)])
    about_text = TextAreaField('Texto "Nosotros"', validators=[Optional()])
    facebook = StringField('Facebook URL', validators=[Optional()])
    instagram = StringField('Instagram URL', validators=[Optional()])
    hero_title = StringField('Título del banner', validators=[Optional(), Length(max=200)])
    hero_subtitle = StringField('Subtítulo del banner', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Guardar configuración')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Contraseña actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar nueva contraseña', validators=[DataRequired()])
    submit = SubmitField('Cambiar contraseña')
    
    def validate_confirm_password(self, field):
        if field.data != self.new_password.data:
            raise ValidationError('Las contraseñas no coinciden')
