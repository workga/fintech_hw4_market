from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.market import exceptions
from app.market.config import CRYPTO_UPDATE_DELTA
from app.market.database import create_session
from app.market.models import Crypto, Operation, Portfolio, User, serialized


def get_users() -> list[dict[str, Any]]:
    try:
        with create_session() as session:
            users = session.query(User).all()
            return serialized(users)

    except exceptions.DatabaseError as error:
        raise exceptions.MarketError("Can't get list of users.") from error


def add_user(login: str) -> None:
    try:
        with create_session() as session:
            session.add(User(login))

    except exceptions.DatabaseError as error:
        raise exceptions.MarketError("Can't register user.") from error


def get_operations(login: str) -> list[dict[str, Any]]:
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

    except exceptions.DatabaseError as error:
        raise exceptions.MarketError("Can't get list of operations.") from error


def add_operation(
    login: str,
    crypto_name: str,
    operation_type: str,
    amount: int,
    time_str: str,
) -> None:
    if amount <= 0:
        raise exceptions.MarketError('Amount must be positive')

    time = datetime.strptime(time_str, """%a, %d %b %Y %H:%M:%S GMT""")

    try:
        with create_session() as session:
            crypto = session.query(Crypto).where(Crypto.name == crypto_name).one()

            # Time check is used for both purchase and sale operations
            if (time - crypto.last_updated) >= CRYPTO_UPDATE_DELTA:
                raise exceptions.MarketError('Crypto exchange rate has been updated')

            user = session.query(User).where(User.login == login).one()

            # import pytest
            # pytest.set_trace()
            if operation_type == 'purchase':
                purchase(session, user, crypto, amount)
            elif operation_type == 'sale':
                sale(session, user, crypto, amount)
            else:
                raise exceptions.MarketError('Wrong operation type')

    except exceptions.DatabaseError as error:
        raise exceptions.MarketError("Can't add operation") from error


def get_balance(login: str) -> dict[str, int]:
    try:
        with create_session() as session:
            balance = (
                session.query(User.balance).where(User.login == login).one().balance
            )
            return {'balance': balance}

    except exceptions.DatabaseError as error:
        raise exceptions.MarketError("Can't get balance.") from error


def get_portfolio(login: str) -> list[dict[str, Any]]:
    try:
        with create_session() as session:
            portfolio = (
                session.query(Portfolio)
                .join(Portfolio.user)
                .where(User.login == login)
                .all()
            )
            return serialized(portfolio)

    except exceptions.DatabaseError as error:
        raise exceptions.MarketError("Can't get portfolio.") from error


def get_crypto() -> list[dict[str, Any]]:
    try:
        with create_session() as session:
            crypto = session.query(Crypto).all()
            return serialized(crypto)

    except exceptions.DatabaseError as error:
        raise exceptions.MarketError("Can't get list of crypto.") from error


def add_crypto(
    crypto_name: str,
    purchase_cost: int,
    sale_cost: int,
) -> None:
    try:
        with create_session() as session:
            session.add(Crypto(crypto_name, purchase_cost, sale_cost))

    except exceptions.DatabaseError as error:
        raise exceptions.MarketError("Can't add crypto.") from error


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


def update_crypto(crypto_name: str, purchase_cost: int, sale_cost: int) -> None:
    try:
        with create_session() as session:
            crypto = session.query(Crypto).where(Crypto.name == crypto_name).one()
            crypto.purchase_cost = purchase_cost
            crypto.sale_cost = sale_cost

    except exceptions.DatabaseError as error:
        raise exceptions.MarketError("Can't update crypto.") from error
