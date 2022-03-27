from flask import Flask

from app.market import database as market_db
from app.market import logger as market_logger
from app.market import routes as market_routes
from app.market import updates


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    market_db.init_db()
    market_db.init_app(app)

    market_logger.init()

    app.register_blueprint(market_routes.bp, url_prefix='/market')

    updates.run_updates()
    return app
