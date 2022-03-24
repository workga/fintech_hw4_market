from contextlib import contextmanager

import click
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.market import exceptions

Base = declarative_base()


def init_db(url):
    engine = create_engine(url)

    global Session
    Session = sessionmaker(bind=engine)


    Base.metadata.create_all(bind=engine)


def init_app(app):
    app.cli.add_command(clear_db_command)


@contextmanager
def create_session(**kwargs):
    session = Session(**kwargs)
    try:
        yield session
        session.commit()
    except SQLAlchemyError as error:
        session.rollback()
        print('ERROR: ', error)
        raise exceptions.DatabaseError(error) from error
    finally:
        session.close()


def clear_db():
    with create_session() as session:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())


@click.command('clear-db')
@with_appcontext
def clear_db_command():
    clear_db()
    click.echo('Database cleared')
