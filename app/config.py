import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    # PostgreSQL: postgresql://user:password@host/dbname
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False