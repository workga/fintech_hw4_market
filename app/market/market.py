from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.market import exceptions
from app.market.config import CRYPTO_UPDATE_DELTA
from app.market.database import db_session
from app.market.models import Crypto, Operation, Portfolio, User, serialized


@db_session
def get_users(session: Session) -> list[dict[str, Any]]:
    users = session.query(User).all()
    return serialized(users)


@db_session
def add_user(login: str, session: Session) -> None:
    session.add(User(login))


@db_session
def get_operations(login: str, session: Session) -> list[dict[str, Any]]:
    operations = (
        session.query(Operation)
        .join(Operation.user)
        .where(User.login == login)
        .order_by(Operation.created)
        .all()
    )
    return serialized(operations)


@db_session
def add_operation(
    login: str,
    crypto_name: str,
    operation_type: str,
    amount: int,
    time_str: str,
    session: Session,
) -> None:
    if amount <= 0:
        raise exceptions.MarketError('Amount must be positive')

    time = datetime.strptime(time_str, """%a, %d %b %Y %H:%M:%S GMT""")

    crypto = session.query(Crypto).where(Crypto.name == crypto_name).one()

    if (time - crypto.last_updated) >= CRYPTO_UPDATE_DELTA:
        raise exceptions.MarketError('Crypto exchange rate has been updated')

    user = session.query(User).where(User.login == login).one()

    if operation_type == 'purchase':
        purchase(session, user, crypto, amount)
    elif operation_type == 'sale':
        sale(session, user, crypto, amount)
    else:
        raise exceptions.MarketError('Wrong operation type')


@db_session
def get_balance(login: str, session: Session) -> dict[str, int]:
    balance = session.query(User.balance).where(User.login == login).one().balance
    return {'balance': balance}


@db_session
def get_portfolio(login: str, session: Session) -> list[dict[str, Any]]:
    portfolio = (
        session.query(Portfolio).join(Portfolio.user).where(User.login == login).all()
    )
    return serialized(portfolio)


@db_session
def get_crypto(session: Session) -> list[dict[str, Any]]:
    crypto = session.query(Crypto).all()
    return serialized(crypto)


@db_session
def add_crypto(
    crypto_name: str,
    purchase_cost: int,
    sale_cost: int,
    session: Session,
) -> None:
    session.add(Crypto(crypto_name, purchase_cost, sale_cost))


def purchase(session: Session, user: User, crypto: Crypto, amount: int) -> None:
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


def sale(session: Session, user: User, crypto: Crypto, amount: int) -> None:
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

    session.add(
        Operation(
            user.id,
            crypto.id,
            'sale',
            amount,
            crypto.purchase_cost,
            crypto.sale_cost,
        )
    )

    portfolio.amount -= amount


@db_session
def update_crypto(
    crypto_name: str, purchase_cost: int, sale_cost: int, session: Session
) -> None:
    crypto = session.query(Crypto).where(Crypto.name == crypto_name).one()
    crypto.purchase_cost = purchase_cost
    crypto.sale_cost = sale_cost
