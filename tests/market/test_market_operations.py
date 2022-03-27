import pytest

from app.market import market
from app.market.config import CRYPTO_UPDATE_DELTA
from app.market.database import create_session
from app.market.exceptions import MarketError
from app.market.models import Crypto, Operation, User
from tests.market.conftest import formatted_now, mock_db_exception


# ----------/ get_operations() /----------
@pytest.mark.parametrize(
    ('user', 'crypto', 'login', 'amount'),
    [
        (User('Annet'), Crypto('Favicoin', 200, 100), 'Annet', 10),
    ],
)
def test_get_operation_success(user, crypto, login, amount):
    with create_session(expire_on_commit=False) as session:
        session.add(user)
        session.add(crypto)

    market.add_operation(user.login, crypto.name, 'purchase', amount, formatted_now())
    market.add_operation(user.login, crypto.name, 'sale', amount, formatted_now())

    operations = market.get_operations(login)
    assert len(operations) == 2
    assert operations[0]['operation_type'] == 'purchase'
    assert operations[1]['operation_type'] == 'sale'


@pytest.mark.parametrize(
    ('user', 'crypto', 'login', 'amount'),
    [
        (User('Annet'), Crypto('Favicoin', 200, 100), 'Annet', 10),
    ],
)
def test_get_operation_db_excepton(mocker, user, crypto, login, amount):
    with create_session(expire_on_commit=False) as session:
        session.add(user)
        session.add(crypto)

    market.add_operation(user.login, crypto.name, 'purchase', amount, formatted_now())
    market.add_operation(user.login, crypto.name, 'sale', amount, formatted_now())

    mock_db_exception(mocker)

    with pytest.raises(MarketError):
        market.get_operations(login)


@pytest.mark.parametrize(
    ('user', 'crypto', 'login', 'amount'),
    [
        (User('Annet'), Crypto('Favicoin', 200, 100), 'Bella', 10),
        (User('Annet'), Crypto('Favicoin', 200, 100), '', 10),
        (User('Annet'), Crypto('Favicoin', 200, 100), None, 10),
        (User('Annet'), Crypto('Favicoin', 200, 100), 'Annet', 0),
    ],
)
def test_get_operation_fail(mocker, user, crypto, login, amount):
    with create_session(expire_on_commit=False) as session:
        session.add(user)
        session.add(crypto)

    if amount > 0:
        market.add_operation(
            user.login, crypto.name, 'purchase', amount, formatted_now()
        )
        market.add_operation(user.login, crypto.name, 'sale', amount, formatted_now())

    mock_db_exception(mocker)

    with pytest.raises(MarketError):
        market.get_operations(login)


# ----------/ add_operation() /----------
@pytest.mark.parametrize(
    ('user', 'crypto', 'amount'),
    [
        (User('Annet'), Crypto('Favicoin', 200, 100), 10),
    ],
)
def test_add_operation_success(user, crypto, amount):
    with create_session(expire_on_commit=False) as session:
        session.add(user)
        session.add(crypto)

    market.add_operation(user.login, crypto.name, 'purchase', amount, formatted_now())
    market.add_operation(user.login, crypto.name, 'sale', amount, formatted_now())

    with create_session() as session:
        operations = (
            session.query(Operation)
            .join(Operation.user)
            .where(User.login == user.login)
            .where(Operation.purchase_cost == crypto.purchase_cost)
            .where(Operation.sale_cost == crypto.sale_cost)
            .where(Operation.amount == amount)
            .order_by(Operation.created)
            .all()
        )
        assert len(operations) == 2
        assert operations[0].operation_type == 'purchase'
        assert operations[1].operation_type == 'sale'


@pytest.mark.parametrize(
    ('user', 'crypto', 'amount'),
    [
        (User('Annet'), Crypto('Favicoin', 200, 100), 10),
    ],
)
def test_add_operation_db_exception(mocker, user, crypto, amount):
    with create_session(expire_on_commit=False) as session:
        session.add(user)
        session.add(crypto)

    market.add_operation(user.login, crypto.name, 'purchase', amount, formatted_now())

    mock_db_exception(mocker)

    with pytest.raises(MarketError):
        market.add_operation(
            user.login, crypto.name, 'purchase', amount, formatted_now()
        )
    with pytest.raises(MarketError):
        market.add_operation(user.login, crypto.name, 'sale', amount, formatted_now())


@pytest.mark.parametrize(
    ('login', 'crypto_name', 'amount'),
    [
        ('Bella', 'Favicoin', 10),
        ('', 'Favicoin', 10),
        (None, 'Favicoin', 10),
        ('Annet', 'Geckcoin', 10),
        ('Annet', '', 10),
        ('Annet', None, 10),
        ('Annet', 'Favicoin', 1000),
        ('Annet', 'Favicoin', 0),
        ('Annet', 'Favicoin', -10),
    ],
)
def test_add_operation_purchase_fail(login, crypto_name, amount):
    with create_session() as session:
        session.add(User('Annet'))
        session.add(Crypto('Favicoin', 200, 100))

    with pytest.raises(MarketError):
        market.add_operation(login, crypto_name, 'purchase', amount, formatted_now())


@pytest.mark.parametrize(
    ('login', 'crypto_name', 'amount'),
    [
        ('Bella', 'Favicoin', 10),
        ('', 'Favicoin', 10),
        (None, 'Favicoin', 10),
        ('Annet', 'Geckcoin', 10),
        ('Annet', '', 10),
        ('Annet', None, 10),
        ('Annet', 'Favicoin', 1000),
        ('Annet', 'Favicoin', 0),
        ('Annet', 'Favicoin', -10),
    ],
)
def test_add_operation_sale_fail(login, crypto_name, amount):
    with create_session(expire_on_commit=False) as session:
        session.add(User('Annet'))
        session.add(Crypto('Favicoin', 200, 100))

    market.add_operation('Annet', 'Favicoin', 'purchase', 10, formatted_now())

    with pytest.raises(MarketError):
        market.add_operation(login, crypto_name, 'sale', amount, formatted_now())


@pytest.mark.parametrize(
    ('login', 'crypto_name', 'amount', 'time_delta'),
    [
        ('Annet', 'Favicoin', 10, CRYPTO_UPDATE_DELTA),
    ],
)
def test_add_operation_time_fail(login, crypto_name, amount, time_delta):
    with create_session() as session:
        session.add(User('Annet'))
        session.add(Crypto('Favicoin', 200, 100))

    market.add_operation('Annet', 'Favicoin', 'purchase', 10, formatted_now())

    with pytest.raises(MarketError):
        market.add_operation(
            login, crypto_name, 'purchase', amount, formatted_now(time_delta)
        )
    with pytest.raises(MarketError):
        market.add_operation(
            login, crypto_name, 'sale', amount, formatted_now(time_delta)
        )
