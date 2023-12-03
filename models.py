from database import db, Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.Integer)
    business_address = db.Column(db.String)
    instance_contract = db.Column(db.String)

    subscriptions = relationship('Subscription', back_populates='user')


class Channel(Base):
    __tablename__ = 'channels'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    author = db.Column(db.String)
    subscription_cost = db.Column(db.Float)

    is_approved = db.Column(db.Boolean, default=True)

    subscriptions = relationship('Subscription', back_populates='channel')


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'))
    duration = db.Column(db.Integer)
    subscription_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='subscriptions')
    channel = relationship('Channel', back_populates='subscriptions')
