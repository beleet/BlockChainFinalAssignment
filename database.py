import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base


engine = db.create_engine('sqlite:///example.db')

session = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
))

Base = declarative_base()
Base.query = session.query_property()
