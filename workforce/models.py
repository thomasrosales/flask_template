from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship
from settings.database import Base
from utils.models import DateAware
# from sales.models import Sale

# Create your model here.


class User(DateAware):
    __tablename__ = 'users'

    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(500), nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_manager = Column(Boolean, default=False, nullable=False)
    is_seller = Column(Boolean, default=True, nullable=False)
    is_costumer = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    manager = relationship("Manager", uselist=False, back_populates="user")
    seller = relationship("Seller", uselist=False, back_populates="user")
    customer = relationship("Costumer", uselist=False, back_populates="user")
    thumbnail = Column(String(256))

    def __init__(self, username, password, is_superuser=False, is_manager=False, is_seller=True, is_costumer=False):
        self.username = username
        self.password = password
        self.is_superuser = is_superuser
        self.is_manager = is_manager
        self.is_seller = is_seller
        self.is_costumer = is_costumer

    def __repr__(self):
        return f'<User {self.username}>'


class Manager(DateAware):
    __tablename__ = 'managers'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="manager")

    def __init__(self, user_id):
        self.user_id = user_id


class Seller(DateAware):
    __tablename__ = 'sellers'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="seller")
    # sale = relationship("Sale")

    def __init__(self, user_id):
        self.user_id = user_id


class Costumer(DateAware):
    __tablename__ = 'costumers'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="customer")

    def __init__(self, user_id):
        self.user_id = user_id
