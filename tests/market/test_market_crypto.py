import pytest

from app.market import market
from app.market.database import create_session
from app.market.exceptions import DatabaseError
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

    assert len(crypto) == count, 'Wrong number of crypto'


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

    with pytest.raises(DatabaseError):
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
        assert crypto.purchase_cost == purchase_cost, 'Returned purchase_cost is wrong'
        assert crypto.sale_cost == sale_cost, 'Returned sale_cost is wrong'


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

    with pytest.raises(DatabaseError):
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

    with pytest.raises(DatabaseError):
        market.add_crypto(crypto_name, purchase_cost, sale_cost)


def test_update_crypto_success():
    with create_session() as session:
        db_crypto = Crypto('Favicoin', 200, 100)
        session.add(db_crypto)

    market.update_crypto('Favicoin', 250, 150)

    with create_session() as session:
        db_crypto = session.query(Crypto).where(Crypto.name == 'Favicoin').one()

        assert db_crypto.purchase_cost == 250, 'purchase_cost updated wrong'
        assert db_crypto.sale_cost == 150, 'sale_cost updated wrong'


def test_update_crypto_db_exception(mocker):
    with create_session() as session:
        db_crypto = Crypto('Favicoin', 200, 100)
        session.add(db_crypto)

        mock_db_exception(mocker)

        with pytest.raises(DatabaseError):
            market.update_crypto('Favicoin', 250, 150)
