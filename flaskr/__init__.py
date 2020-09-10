from flask import Flask
from settings.settings import DevelopmentConfig
from settings.database import session
from settings.logger_config import LOGGING
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
import logging
import logging.config


# APPLICATION CONFIGURATION

logging.config.dictConfig(LOGGING)

bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config=None):

    app = Flask(__name__, instance_relative_config=True)

    bcrypt.init_app(app)

    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(DevelopmentConfig())

    # jwt = JWTManager(app)
    jwt.init_app(app)

    # MODULES

    from workforce.workforce import workforce
    from authentication.authentication import authentication

    # BLUEPRINT

    app.register_blueprint(authentication,  url_prefix='/authentication')
    app.register_blueprint(workforce,  url_prefix='/workforce')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        session.remove()

    return app
