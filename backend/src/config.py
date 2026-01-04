import os

class Config:
    TESTING = False
    
class DevelopmentConfig(Config):
    CACHE_TYPE="SimpleCache"
    CACHE_DEFAULT_TIMEOUT=3600
    # CORS
    cors_allow_all: bool = os.getenv("CORS_ALLOW_ALL", "true").lower() == "true"
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")  # comma-separated

