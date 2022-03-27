from datetime import timedelta

CRYPTO_UPDATE_DELTA = timedelta(seconds=10)
DATETIME_FORMAT = """%a, %d %b %Y %H:%M:%S GMT"""

MARKET_LOGGER_NAME = 'market_logger'
MARKET_LOGGER_LEVEL = 'DEBUG'
MARKET_DB_URL = 'sqlite:///app.market.sqlite'
MARKET_DB_URL_TEST = 'sqlite:///app.market.testing.sqlite'
