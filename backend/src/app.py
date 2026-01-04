import os

from flask import Flask
from flask_caching import Cache

from .config import Config, DevelopmentConfig


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

    # ensure the instance config folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    cache = Cache(app)
    logger.info('Cache created.')

    from .routes import auth, transactions
    app.register_blueprint(auth.bp)
    app.register_blueprint(transactions.bp)

    logger.info('Registered blueprints.')

    return app


app = create_app()
if __name__ == '__main__':
    cfg = Config.get_instance()
    port = int(os.getenv("PORT", cfg.port))
    app.run(host=cfg.host, port=port, debug=cfg.debug)