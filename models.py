from database import db, Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.Integer)
    business_address_mumbai = db.Column(db.String)
    business_address_sepolia = db.Column(db.String)
    instance_contract_mumbai = db.Column(db.String)
    instance_contract_sepolia = db.Column(db.String)

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

    user = relationship('User', back_populates='subscriptions')
    channel = relationship('Channel', back_populates='subscriptions')
