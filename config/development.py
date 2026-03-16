import os


class DevelopmentConfig:
    DEBUG                  = True
    SECRET_KEY             = os.getenv('SECRET_KEY', 'dev-secret-change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///bakery_dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLOUDINARY_CLOUD_NAME  = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY     = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET  = os.getenv('CLOUDINARY_API_SECRET')
