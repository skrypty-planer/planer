import os

from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
import os

from .config import DevelopmentConfig

def create_app(test_config=None):
    # configure logger
    from .error_handling.logger import configure_logger, logger
    configure_logger()

    logger.info('Logger configured.')

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # set up flask.session
    app.config["SECRET_KEY"] = "super-secret-key"  # lazy - "good enough for now"
    app.config["SESSION_COOKIE_HTTPONLY"] = True   

    logger.info('App created.')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(DevelopmentConfig())
        logger.info('Loaded configuration.')
    else:
        # load the test config if passed in
        app.config.from_object(test_config)
        logger.info('Loaded test configuration.')
    
    cors_allow_all: bool = os.getenv("CORS_ALLOW_ALL", "true").lower() == "true"
    if cors_allow_all:
        CORS(app)
    else:
        CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

    cache = Cache(app)
    cache.set("users", dict())
    logger.info('Cache created.')

    from .routes import auth, transactions, health
    app.register_blueprint(auth.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(health.bp)

    logger.info('Registered blueprints.')

    from .utilities.AuthManager import AuthManager
    from .utilities.CacheManager import CacheManager
    from .utilities.TransactionManager import TransactionManager
    AuthManager()
    CacheManager(cache)
    TransactionManager()
    
    logger.info('Created singleton objects.')

    app.pending_errors = []

    return app


app = create_app()
if __name__ == '__main__':
    cfg = DevelopmentConfig()
    port = int(os.getenv("PORT", cfg.port))
    app.run(host=cfg.host, port=port, debug=cfg.debug)
