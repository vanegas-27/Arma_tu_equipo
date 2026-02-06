# create_db.py
from app import app, db
from app import models

with app.app_context():
    db.create_all()
    print("✅ Tablas creadas correctamente en la base de datos.")