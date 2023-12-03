from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    role = Column(String)
    telegram_id = Column(Integer)
    registration_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_banned_by_admin = Column(Boolean, default=False)
    balance = Column(Float)

    subscriptions = relationship('Subscription', back_populates='user')


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    author = Column(Integer)
    subscription_cost = Column(Float)

    is_approved = Column(Boolean, default=True)
    number_of_subscribers = Column(Integer)
    creation_timestamp = Column(DateTime(timezone=True))

    subscriptions = relationship('Subscription', back_populates='channel')


class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    channel_id = Column(Integer, ForeignKey('channels.id'))
    duration = Column(Integer)
    subscription_timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='subscriptions')
    channel = relationship('Channel', back_populates='subscriptions')
#
# заменить сабскрипшнс на транзакции
# добавить возможноть иметь несколько подписок на канал
