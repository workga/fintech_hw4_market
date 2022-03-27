import pytest

from app.market import market
from app.market.database import create_session
from app.market.exceptions import MarketError
from app.market.models import User
from tests.market.conftest import mock_db_exception


# ----------/ get_users() /----------
@pytest.mark.parametrize(
    ('stored_users', 'count'),
    [
        ([], 0),
        ([User('Annet')], 1),
        ([User('Annet'), User('Bella')], 2),
    ],
)
def test_get_users_success(stored_users, count):
    with create_session() as session:
        for user in stored_users:
            session.add(user)

    users = market.get_users()

    assert len(users) == count


@pytest.mark.parametrize(
    'stored_users',
    [
        [],
        [User('Annet')],
        [User('Annet'), User('Bella')],
    ],
)
def test_get_users_db_exception(mocker, stored_users):
    with create_session() as session:
        for user in stored_users:
            session.add(user)

    mock_db_exception(mocker)

    with pytest.raises(MarketError):
        market.get_users()


# ----------/ add_user() /----------
@pytest.mark.parametrize(
    ('stored_users', 'login'),
    [
        ([], 'Annet'),
        ([User('Annet')], 'Bella'),
        ([User('Annet'), User('Bella')], 'Clare'),
    ],
)
def test_add_user_success(stored_users, login):
    with create_session() as session:
        for user in stored_users:
            session.add(user)

    market.add_user(login)

    with create_session() as session:
        user = session.query(User).where(User.login == login).one()
        assert user.balance == 1000 * 100


@pytest.mark.parametrize(
    ('stored_users', 'login'),
    [
        ([], 'Annet'),
        ([User('Annet')], 'Bella'),
        ([User('Annet'), User('Bella')], 'Clare'),
    ],
)
def test_add_user_db_exception(mocker, stored_users, login):
    with create_session() as session:
        for user in stored_users:
            session.add(user)

    mock_db_exception(mocker)

    with pytest.raises(MarketError):
        market.add_user(login)


@pytest.mark.parametrize(
    ('stored_users', 'login'),
    [
        ([], ''),
        ([User('Annet')], ''),
        ([User('Annet')], 'Annet'),
        ([User('Annet'), User('Bella')], 'Bella'),
    ],
)
def test_add_user_fail(stored_users, login):
    with create_session() as session:
        for user in stored_users:
            session.add(user)

    with pytest.raises(MarketError):
        market.add_user(login)
