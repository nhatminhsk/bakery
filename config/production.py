import os


class ProductionConfig:
    DEBUG      = False
    SECRET_KEY = os.getenv('SECRET_KEY')

    _db_url = os.getenv('DATABASE_URL', '')
    # Render dùng prefix "postgres://" cũ, SQLAlchemy cần "postgresql://"
    SQLALCHEMY_DATABASE_URI = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLOUDINARY_CLOUD_NAME  = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY     = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET  = os.getenv('CLOUDINARY_API_SECRET')
