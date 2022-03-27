import logging

from app.market.config import MARKET_LOGGER_LEVEL, MARKET_LOGGER_NAME


def init() -> None:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter(
            '%(levelname)s %(asctime)s %(funcName)s(%(lineno)d) %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S',
        )
    )

    market_logger = logging.getLogger(MARKET_LOGGER_NAME)
    market_logger.addHandler(stream_handler)
    market_logger.setLevel(MARKET_LOGGER_LEVEL)


def get_logger() -> logging.Logger:
    return logging.getLogger(MARKET_LOGGER_NAME)
