from datetime import datetime


from app.market import exceptions
from app.market.config import CRYPTO_UPDATE_DELTA
from app.market.database import create_session
from app.market.models import Crypto, Operation, Portfolio, User, serialized


def get_users():
    try:
        with create_session() as session:
            users = session.query(User).all()
            return serialized(users)

    except exceptions.DatabaseError:
        raise exceptions.MarketError("Can't get list of users.")


def add_user(login):
    try:
        with create_session() as session:
            session.add(User(login))

    except exceptions.DatabaseError:
        raise exceptions.MarketError("Can't register user.")


def get_operations(login):
    try:
        with create_session() as session:
            operations = (
                session.query(Operation)
                .join(Operation.user)
                .where(User.login == login)
                .order_by(Operation.created)
                .all()
            )
            return serialized(operations)

    except exceptions.DatabaseError:
        raise exceptions.MarketError("Can't get list of operations.")


def add_operation(login, crypto_name, operation_type, amount, time):
    if amount <= 0:
        raise exceptions.MarketError('Amount must be positive')

    time = datetime.strptime(time, """%a, %d %b %Y %H:%M:%S GMT""")

    try:
        with create_session() as session:
            crypto = session.query(Crypto).where(Crypto.name == crypto_name).one()

            if (time - crypto.last_updated) > CRYPTO_UPDATE_DELTA:
                raise exceptions.MarketError('Crypto exchange rate has been updated')

            user = session.query(User).where(User.login == login).one()

            if operation_type == 'purchase':
                purchase(session, user, crypto, amount)
            elif operation_type == 'sale':
                sale(session, user, crypto, amount)
            else:
                raise exceptions.MarketError('Wrong operation type')

    except exceptions.DatabaseError as error:
        raise exceptions.MarketError("Can't add operation") from error


def get_balance(login):
    try:
        with create_session() as session:
            balance = (
                session.query(User.balance).where(User.login == login).one().balance
            )
            return {'balance': balance}

    except exceptions.DatabaseError:
        raise exceptions.MarketError("Can't get balance.")


def get_portfolio(login):
    try:
        with create_session() as session:
            portfolio = (
                session.query(Portfolio)
                .join(Portfolio.user)
                .where(User.login == login)
                .all()
            )
            return serialized(portfolio)

    except exceptions.DatabaseError:
        raise exceptions.MarketError("Can't get portfolio.")


def get_crypto():
    try:
        with create_session(expire_on_commit=False) as session:
            crypto = session.query(Crypto).all()
            return serialized(crypto)

    except exceptions.DatabaseError:
        raise exceptions.MarketError("Can't get list of crypto.")


def add_crypto(crypto_name, purchase_cost, sale_cost):
    try:
        with create_session() as session:
            session.add(Crypto(crypto_name, purchase_cost, sale_cost))

    except exceptions.DatabaseError:
        raise exceptions.MarketError("Can't add crypto.")


def purchase(session, user, crypto, amount):
    if user.balance < crypto.purchase_cost * amount:
        raise exceptions.MarketError('Not enough money to purchase')

    user.balance -= crypto.purchase_cost * amount

    session.add(
        Operation(
            user.id,
            crypto.id,
            'purchase',
            amount,
            crypto.purchase_cost,
            crypto.sale_cost,
        )
    )

    # Using 'first()' because we just create portfolio if portfolio doesn't exist
    portfolio = (
        session.query(Portfolio)
        .where(Portfolio.user_id == user.id)
        .where(Portfolio.crypto_id == crypto.id)
        .first()
    )

    if portfolio is None:
        session.add(Portfolio(user.id, crypto.id, amount))
    else:
        portfolio.amount += amount


def sale(session, user, crypto, amount):
    # Using 'first()' because we raise MarketError if portfolio doesn't exist
    portfolio = (
        session.query(Portfolio)
        .where(Portfolio.user_id == user.id)
        .where(Portfolio.crypto_id == crypto.id)
        .first()
    )

    if portfolio is None or portfolio.amount < amount:
        raise exceptions.MarketError('Not enough crypto to sale')

    user.balance += crypto.sale_cost * amount
    portfolio.amount -= amount
