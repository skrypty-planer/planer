class Config:
    TESTING = False

class DevelopmentConfig(Config):
    CACHE_TYPE="SimpleCache"
    CACHE_DEFAULT_TIMEOUT=60
