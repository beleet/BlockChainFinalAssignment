from database import db, Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String)
    telegram_id = db.Column(db.Integer)
    registration_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    is_banned_by_admin = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Float)

    subscriptions = relationship('Subscription', back_populates='user')


class Channel(Base):
    __tablename__ = 'channels'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer)
    subscription_cost = db.Column(db.Float)

    is_approved = db.Column(db.Boolean, default=True)
    number_of_subscribers = db.Column(db.Integer)
    creation_timestamp = db.Column(db.DateTime(timezone=True))

    subscriptions = relationship('Subscription', back_populates='channel')


class Transactions(Base):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'))
    duration = db.Column(db.Integer)
    subscription_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='subscriptions')
    channel = relationship('Channel', back_populates='subscriptions')
