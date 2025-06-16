from contextlib import contextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session

from db import DB

engine = DB().engine

SessionFactory = sessionmaker(bind=engine)

Session = scoped_session(SessionFactory)


@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()
