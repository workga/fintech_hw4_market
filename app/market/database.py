from contextlib import contextmanager

import click
from flask import Flask
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.market import exceptions
from app.market.config import MARKET_DB_URL
from app.market.logger import get_logger

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
    except exceptions.DatabaseError as error:
        session.rollback()
        get_logger().error(error)
        raise
    finally:
        session.close()


def clear_db() -> None:
    with create_session() as session:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
    get_logger().info('Database cleared')


@click.command('clear-db')
@with_appcontext
def clear_db_command() -> None:
    '''
    Clear database
    '''
    clear_db()
