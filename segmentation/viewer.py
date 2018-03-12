from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os


Base = declarative_base()
basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, "article.db"))
DBSession = sessionmaker(bind=engine)


class Art(Base):
    __tablename__ = "art"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    url = Column(String)


class IDF(Base):
    __tablename__ = "idf"
    id = Column(Integer, primary_key=True)
    word = Column(String)
    value = Column(Integer)


def create():
    Base.metadata.create_all(engine)
