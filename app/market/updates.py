import threading
import time
from random import randint

from app.market import exceptions, market
from app.market.config import CRYPTO_UPDATE_DELTA
from app.market.logger import get_logger


def update_rates() -> None:
    while True:
        time.sleep(CRYPTO_UPDATE_DELTA.seconds)

        try:
            crypto = market.get_crypto()
            for crypt in crypto:
                new_purchase_cost = int(
                    crypt['purchase_cost'] * (1 + randint(-10, 10) / 100)
                )
                new_sale_cost = int(crypt['sale_cost'] * (1 + randint(-10, 10) / 100))
                market.update_crypto(
                    crypt['name'], max(new_purchase_cost, 1), max(new_sale_cost, 1)
                )

        except exceptions.MarketError as error:
            get_logger().error(error)


def run_updates() -> None:
    updates_thread = threading.Thread(target=update_rates, daemon=True)
    updates_thread.start()
