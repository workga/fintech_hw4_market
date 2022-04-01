from datetime import datetime, timedelta

import pytest

from app.market.config import DATETIME_FORMAT, MARKET_DB_URL_TEST
from app.market.database import clear_db, init_db
from app.market.exceptions import DatabaseError


@pytest.fixture(name='client')
def ficture_client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def db():
    init_db(MARKET_DB_URL_TEST)
    clear_db()
    yield
    clear_db()


# def fill_db():
#     with create_session() as session:
#         session.add(User('Annet'))
#         session.add(User('Bella'))
#         session.add(User('Clare'))
#         session.add(User('Diana'))
#         session.add(User('Elena'))

#         session.add(Crypto('Favicoin', 200, 100))
#         session.add(Crypto('Geckcoin', 400, 200))
#         session.add(Crypto('Hellcoin', 600, 300))
#         session.add(Crypto('Ironcoin', 800, 400))
#         session.add(Crypto('Jamcoin', 1000, 500))


def mock_db_exception(mocker):
    mocker.patch('sqlalchemy.orm.Session.add', side_effect=DatabaseError)
    mocker.patch('sqlalchemy.orm.Query.all', side_effect=DatabaseError)
    mocker.patch('sqlalchemy.orm.Query.one', side_effect=DatabaseError)
    mocker.patch('sqlalchemy.orm.Query.first', side_effect=DatabaseError)
    mocker.patch('sqlalchemy.orm.Query.one_or_none', side_effect=DatabaseError)


def formatted_now(time_shift=timedelta()):
    return datetime.strftime(datetime.utcnow() + time_shift, DATETIME_FORMAT)
