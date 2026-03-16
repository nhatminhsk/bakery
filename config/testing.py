class TestingConfig:
    TESTING                 = True
    DEBUG                   = True
    SECRET_KEY              = 'test-secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED        = False
