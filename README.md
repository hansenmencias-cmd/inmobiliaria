# 🏠 Premium Real Estate Platform

Plataforma web inmobiliaria profesional, moderna y completamente administrable.

## Características

- ✅ Catálogo público de propiedades (casas, apartamentos, solares, locales, fincas, oficinas...)
- ✅ Buscador avanzado con filtros (precio, ciudad, tipo, habitaciones, baños, estado...)
- ✅ Página individual por propiedad con URL amigable (`/propiedad/casa-moderna-tegucigalpa`)
- ✅ Galería de fotos con lightbox, zoom y navegación táctil
- ✅ Soporte de videos
- ✅ Panel de administración completo (sin tocar código)
- ✅ Subida de fotos y videos desde iPhone, Samsung, Android o PC
- ✅ Estados: Disponible / Vendida / Alquilada / Reservada
- ✅ Estadísticas (vistas, totales, más visitadas)
- ✅ Formulario de contacto + botón flotante WhatsApp
- ✅ Mapas (OpenStreetMap / Google Maps)
- ✅ SEO + Open Graph para compartir en WhatsApp/Facebook
- ✅ Modo claro / oscuro
- ✅ 100% responsive (móvil, tablet, desktop)
- ✅ Diseño premium (azul oscuro, blanco, acentos dorados)

---

## Instalación local

### 1. Requisitos
- Python 3.10+
- pip

### 2. Instalar dependencias

```bash
cd inmobiliaria
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Ejecutar

```bash
python run.py
```

Abre en el navegador:
- **Sitio público:** http://127.0.0.1:5000
- **Panel admin:** http://127.0.0.1:5000/admin

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **Cambia la contraseña inmediatamente** desde el panel (menú → Cambiar contraseña).

---

## Cómo administrar (sin código)

1. Entra a `/admin` e inicia sesión.
2. Ve a **Agregar propiedad**.
3. Completa título, descripción, precio, ubicación, etc.
4. Sube la foto principal y las fotos adicionales (puedes seleccionar varias a la vez desde la galería del teléfono).
5. Opcionalmente sube videos.
6. Pulsa **Guardar propiedad**.
7. La propiedad aparece automáticamente en el sitio público.

Puedes:
- Editar cualquier dato, precio, estado, fotos y videos.
- Marcar como Vendida / Alquilada / Reservada / Disponible.
- Eliminar propiedades (con confirmación).
- Cambiar el número de WhatsApp y datos de la empresa en **Configuración**.

---

## Publicar en internet

### Opción A: Render.com (recomendada, gratuita)

1. Crea una cuenta en [render.com](https://render.com).
2. New → Web Service.
3. Conecta tu repositorio Git (sube este proyecto a GitHub).
4. Configuración:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
   - **Environment:** Python 3
5. Añade variable de entorno:
   - `SECRET_KEY` = una cadena larga y aleatoria
   - `FLASK_CONFIG` = `production`
6. Deploy.

Tu sitio quedará en: `https://tu-proyecto.onrender.com`

### Opción B: Railway / PythonAnywhere / VPS

- Railway: similar a Render, conecta GitHub.
- PythonAnywhere: sube los archivos y configura un WSGI.
- VPS (DigitalOcean, Contabo, etc.):
  ```bash
  gunicorn -w 4 -b 0.0.0.0:8000 run:app
  ```
  Usa Nginx como reverse proxy + HTTPS (Let's Encrypt).

### Base de datos en producción

Por defecto usa SQLite (perfecto para empezar).  
Para MySQL o PostgreSQL:

```bash
# PostgreSQL
export DATABASE_URL=postgresql://user:pass@host:5432/inmobiliaria

# MySQL
export DATABASE_URL=mysql+pymysql://user:pass@host:3306/inmobiliaria
```

La aplicación detecta automáticamente la URL.

---

## Estructura del proyecto

```
inmobiliaria/
├── app/
│   ├── __init__.py          # Factory de la aplicación
│   ├── models.py            # Modelos (Property, User, Images, Videos...)
│   ├── forms.py             # Formularios WTForms
│   ├── utils.py             # Utilidades (subida de archivos, optimización)
│   ├── routes/
│   │   ├── public.py        # Rutas públicas
│   │   └── admin.py         # Panel de administración
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── uploads/         # Imágenes y videos
│   └── templates/           # HTML
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

---

## Seguridad

- Panel admin protegido con login y sesiones.
- Contraseñas hasheadas (Werkzeug).
- Validación de tipos de archivo en subidas.
- Protección CSRF en formularios.
- Rutas admin no accesibles sin autenticación.

**Antes de producción:**
1. Cambia `SECRET_KEY` en variables de entorno.
2. Cambia la contraseña del admin.
3. Activa `SESSION_COOKIE_SECURE = True` (HTTPS).
4. Considera un CDN para las imágenes.

---

## Personalización rápida

- **Colores:** edita las variables CSS en `app/static/css/style.css` (`:root`).
- **Nombre de empresa, WhatsApp, etc.:** desde el panel → Configuración.
- **Tipos de propiedad:** se pueden ampliar en `models.py` y `forms.py`.

---

## Soporte

Este proyecto está listo para producción.  
El propietario puede gestionar todo el contenido desde el panel sin necesidad de tocar código.

¡Éxito con tu inmobiliaria!
