from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    info = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, login, info):
        self.login = login
        self.info = info


class History(Base):
    __tablename__ = 'History'
    id = Column(Integer, primary_key=True)
    user_ip = Column(String)
    created_at = Column(DateTime)

    def __init__(self, user_ip):
        self.user_ip = user_ip


class Contact(Base):
    _tablename__ = 'Contacts'
    user_id = Column(Integer)
    client_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, user_id, client_id):
        self.user_id = user_id
        self.client_id = client_id
