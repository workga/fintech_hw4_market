import pytest

from app.market import market
from app.market.database import create_session
from app.market.exceptions import MarketError
from app.market.models import Crypto
from tests.market.conftest import mock_db_exception


# ----------/ get_crypto() /-----------
@pytest.mark.parametrize(
    ('stored_crypto', 'count'),
    [
        ([], 0),
        ([Crypto('Favicoin', 200, 100)], 1),
        ([Crypto('Favicoin', 200, 100), Crypto('Geckcoin', 400, 200)], 2),
    ],
)
def test_get_crypto_success(stored_crypto, count):
    with create_session() as session:
        for crypto in stored_crypto:
            session.add(crypto)

    crypto = market.get_crypto()

    assert len(crypto) == count


@pytest.mark.parametrize(
    'stored_crypto',
    [
        [],
        [Crypto('Favicoin', 200, 100)],
        [Crypto('Favicoin', 200, 100), Crypto('Geckcoin', 400, 200)],
    ],
)
def test_get_crypto_db_exception(mocker, stored_crypto):
    with create_session() as session:
        for crypto in stored_crypto:
            session.add(crypto)

    mock_db_exception(mocker)

    with pytest.raises(MarketError):
        market.get_crypto()


# ----------/ add_crypto() /----------
@pytest.mark.parametrize(
    ('stored_crypto', 'crypto_name', 'purchase_cost', 'sale_cost'),
    [
        ([], 'Favicoin', 200, 100),
        ([Crypto('Favicoin', 200, 100)], 'Geckcoin', 400, 200),
        (
            [Crypto('Favicoin', 200, 100), Crypto('Geckcoin', 400, 200)],
            'Hellcoin',
            600,
            300,
        ),
    ],
)
def test_add_crypto_success(stored_crypto, crypto_name, purchase_cost, sale_cost):
    with create_session() as session:
        for crypto in stored_crypto:
            session.add(crypto)

    market.add_crypto(crypto_name, purchase_cost, sale_cost)

    with create_session() as session:
        crypto = session.query(Crypto).where(Crypto.name == crypto_name).one()
        assert crypto.purchase_cost == purchase_cost
        assert crypto.sale_cost == sale_cost


@pytest.mark.parametrize(
    ('stored_crypto', 'crypto_name', 'purchase_cost', 'sale_cost'),
    [
        ([Crypto('Favicoin', 400, 200)], 'Favicoin', 200, 100),
        ([], '', 200, 100),
        ([], None, 200, 100),
        ([], 'Favicoin', 0, 200),
        ([], 'Favicoin', -10, 100),
        ([], 'Favicoin', None, 200),
        ([], 'Favicoin', 600, 0),
        ([], 'Favicoin', 400, -10),
        ([], 'Favicoin', 600, None),
    ],
)
def test_add_crypto_fail(stored_crypto, crypto_name, purchase_cost, sale_cost):
    with create_session() as session:
        for crypto in stored_crypto:
            session.add(crypto)

    with pytest.raises(MarketError):
        market.add_crypto(crypto_name, purchase_cost, sale_cost)


@pytest.mark.parametrize(
    ('stored_crypto', 'crypto_name', 'purchase_cost', 'sale_cost'),
    [
        ([], 'Favicoin', 200, 100),
        ([Crypto('Favicoin', 200, 100)], 'Geckcoin', 400, 200),
        (
            [Crypto('Favicoin', 200, 100), Crypto('Geckcoin', 400, 200)],
            'Hellcoin',
            600,
            300,
        ),
    ],
)
def test_add_crypto_db_exception(
    mocker, stored_crypto, crypto_name, purchase_cost, sale_cost
):
    with create_session() as session:
        for crypto in stored_crypto:
            session.add(crypto)

    mock_db_exception(mocker)

    with pytest.raises(MarketError):
        market.add_crypto(crypto_name, purchase_cost, sale_cost)
