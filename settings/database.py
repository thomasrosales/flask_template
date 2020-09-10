from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from pathlib import Path

SETTING_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent

database = "sqlite:///" + os.path.join(SETTING_PATH, 'db.sqlite')

engine = create_engine(
    database,
    convert_unicode=False,
    connect_args={'check_same_thread': False}
)

session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

Base = declarative_base()
Base.query = session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import utils.models
    import workforce.models
    import authentication.models
    Base.metadata.create_all(bind=engine)


def drop_db():
    Base.metadata.drop_all(bind=engine)
