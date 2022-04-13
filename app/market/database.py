from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, TypeVar, cast

import click
from flask import Flask
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.market import exceptions
from app.market.config import MARKET_DB_URL
from app.market.logger import get_logger

F = TypeVar('F', bound=Callable[..., Any])

Base = declarative_base()
SessionFactory = sessionmaker()


def init_db(url: str = MARKET_DB_URL) -> None:
    engine = create_engine(url)

    SessionFactory.configure(bind=engine)

    Base.metadata.create_all(bind=engine)


def init_app(app: Flask) -> None:
    app.cli.add_command(clear_db_command)


@contextmanager
def create_session(**kwargs: int) -> Session:
    try:
        session = SessionFactory(**kwargs)
        yield session
        session.commit()
    except SQLAlchemyError as error:
        session.rollback()
        get_logger().error(error)
        raise exceptions.DatabaseError(error) from error
    finally:
        session.close()


def db_session(func: F) -> F:
    @wraps(func)
    def wrapper(*args: int, **kwargs: int) -> Any:
        with create_session() as session:
            return func(*args, session=session, **kwargs)

    return cast(F, wrapper)


def clear_db() -> None:
    with create_session() as session:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())


@click.command('clear-db')
@with_appcontext
def clear_db_command() -> None:
    '''
    Clear database
    '''
    clear_db()
