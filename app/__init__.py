from flask import Flask

from app.market import database as market_db
from app.market import routes as market_routes


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    market_db.init_db(app.config['MARKET_DB_URL'])
    market_db.init_app(app)

    app.register_blueprint(market_routes.bp, url_prefix='/market')

    return app
