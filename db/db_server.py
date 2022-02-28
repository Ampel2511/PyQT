from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///ServerDB.sql')
Session = sessionmaker(bind=engine)


class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    info = Column(String)
    pswd = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, login, info, pswd):
        self.login = login
        self.info = info
        self.pswd = pswd


class History(Base):
    __tablename__ = 'History'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    from_user_id = Column(Integer)
    to_user_id = Column(Integer)
    message_text = Column(String)
    created_at = Column(DateTime)

    def __init__(self, chat_id, from_user_id, to_user_id, message_text):
        self.chat_id = chat_id
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.message_text = message_text


class Contacts(Base):
    __tablename__ = 'Contacts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    client_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, user_id, client_id):
        self.user_id = user_id
        self.client_id = client_id


class Chats(Base):
    __tablename__ = 'Chats'
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer)
    to_user_id = Column(Integer)
    created_at = Column(DateTime)

    def __init__(self, from_user_id, to_user_id):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id


Base.metadata.create_all(engine)
session = Session()
