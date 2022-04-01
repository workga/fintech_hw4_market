import pytest

from app.market import market
from app.market.database import create_session
from app.market.exceptions import MarketError
from app.market.models import Crypto, User
from tests.market.conftest import formatted_now, mock_db_exception


def test_get_portfolio_success():
    with create_session() as session:
        db_user = User('Annet')
        session.add(db_user)
        db_crypto = Crypto('Favicoin', 200, 100)
        session.add(db_crypto)
        db_crypto = Crypto('Geckcoin', 400, 200)
        session.add(db_crypto)

    market.add_operation('Annet', 'Favicoin', 'purchase', 10, formatted_now())
    market.add_operation('Annet', 'Favicoin', 'sale', 2, formatted_now())
    market.add_operation('Annet', 'Geckcoin', 'purchase', 10, formatted_now())
    market.add_operation('Annet', 'Geckcoin', 'sale', 2, formatted_now())

    assert len(market.get_portfolio('Annet')) == 2


def test_get_portfolio_fail(mocker):
    with create_session() as session:
        db_user = User('Annet')
        session.add(db_user)
        db_crypto = Crypto('Favicoin', 200, 100)
        session.add(db_crypto)
        db_crypto = Crypto('Geckcoin', 400, 200)
        session.add(db_crypto)

    market.add_operation('Annet', 'Favicoin', 'purchase', 10, formatted_now())
    market.add_operation('Annet', 'Favicoin', 'sale', 2, formatted_now())
    market.add_operation('Annet', 'Geckcoin', 'purchase', 10, formatted_now())
    market.add_operation('Annet', 'Geckcoin', 'sale', 2, formatted_now())

    mock_db_exception(mocker)

    with pytest.raises(MarketError):
        market.get_portfolio('Annet')
