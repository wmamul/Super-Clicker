from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.exceptions import DatabaseError

engine = create_engine('sqlite:///../db.sqlite3', echo=True)
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise DatabaseError('Commiting session raised an exception')
    finally:
        session.close()
