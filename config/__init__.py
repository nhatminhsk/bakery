from config.development import DevelopmentConfig
from config.production import ProductionConfig
from config.testing import TestingConfig

config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
}
