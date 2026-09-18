#!/usr/bin/env python3
"""
Premium Real Estate Platform
Run: python run.py
"""
import os
from app import create_app

app = create_app(os.environ.get('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_CONFIG', 'development') == 'development'
    print(f"""
    ========================================
     Premium Real Estate Platform
    ========================================
     Local:    http://127.0.0.1:{port}
     Admin:    http://127.0.0.1:{port}/admin
     Usuario:  admin
     Password: admin123  (¡cámbiala!)
    ========================================
    """)
    app.run(host='0.0.0.0', port=port, debug=debug)
