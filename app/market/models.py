from typing import Any

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.market.database import Base


def serialized(model: Base) -> Any:
    if isinstance(model, list):
        return [serialized(o) for o in model]

    return {c.name: getattr(model, c.name) for c in model.__table__.columns}


# 'amount', 'balance', 'purchase_cost' and 'sale_cost' are
# multiplied by 100 and stored as integers.
# For example 1005.45 units of some crypto turns into 100545


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String(50), nullable=False, unique=True)
    balance = Column(Integer, default=1000 * 100)

    __table_args__ = (
        CheckConstraint('login != ""'),
        CheckConstraint('balance >= 0'),
    )

    def __init__(self, login: str) -> None:
        self.login = login


class Crypto(Base):
    __tablename__ = 'crypto'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    purchase_cost = Column(Integer, nullable=False)
    sale_cost = Column(Integer, nullable=False)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('name != ""'),
        CheckConstraint('purchase_cost > 0'),
        CheckConstraint('sale_cost > 0'),
    )

    def __init__(
        self,
        name: str,
        purchase_cost: int,
        sale_cost: int,
    ) -> None:
        self.name = name
        self.purchase_cost = purchase_cost
        self.sale_cost = sale_cost


class Portfolio(Base):
    __tablename__ = 'portfolio'

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    crypto_id = Column(Integer, ForeignKey('crypto.id'), nullable=False)
    amount = Column(Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'crypto_id'),
        CheckConstraint('amount >= 0'),
    )

    user = relationship('User', lazy='joined')

    def __init__(self, user_id: int, crypto_id: int, amount: int) -> None:
        self.user_id = user_id
        self.crypto_id = crypto_id
        self.amount = amount


class Operation(Base):
    __tablename__ = 'operation'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    crypto_id = Column(Integer, ForeignKey('crypto.id'), nullable=False)

    operation_type = Column(String(10), nullable=False)
    amount = Column(Integer, nullable=False)

    purchase_cost = Column(Integer, nullable=False)
    sale_cost = Column(Integer, nullable=False)

    created = Column(DateTime, default=func.now())

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id', 'crypto_id'],
            ['portfolio.user_id', 'portfolio.crypto_id'],
        ),
        CheckConstraint('operation_type in ("sale", "purchase")'),
        CheckConstraint('amount >= 0'),
        CheckConstraint('purchase_cost > 0'),
        CheckConstraint('sale_cost > 0'),
    )

    user = relationship('User', lazy='joined')

    def __init__(
        self,
        user_id: int,
        crypto_id: int,
        operation_type: str,
        amount: int,
        purchase_cost: int,
        sale_cost: int,
    ) -> None:
        self.user_id = user_id
        self.crypto_id = crypto_id

        self.operation_type = operation_type

        self.amount = amount
        self.purchase_cost = purchase_cost
        self.sale_cost = sale_cost
