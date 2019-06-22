from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random
import string
from itsdangerous import(
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()
secret_key = ''.join(random.choice(
    string.ascii_uppercase + string.digits) for x in range(32))


class User(Base):
    __tablename__ = 'user'

    name = Column(String(64), index=True)
    mail = Column(String(64), primary_key=True)
    password_hash = Column(String(256))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'mail': self.mail
        }


class Food(Base):
    __tablename__ = 'food'

    name = Column(String(64), primary_key=True)
    image = Column(String(128))
    calorie = Column(Integer, default=0)
    carb = Column(Float, default=0)
    protein = Column(Float, default=0)
    fat = Column(Float, default=0)
    health_point = Column(Integer, default=0)
    category = Column(Integer, default=0)
    description = Column(String(1000))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'image': self.image,
            'calorie': self.calorie,
            'carb': self.carb,
            'protein': self.protein,
            'fat': self.fat,
            'health_point': self.health_point,
            'category': self.category,
            'description': self.description
        }


class Recipe(Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    image = Column(String(128))
    rating = Column(Integer, default=0)
    calorie = Column(Integer, default=0)
    carb = Column(Float, default=0)
    protein = Column(Float, default=0)
    fat = Column(Float, default=0)
    cooking_minutes = Column(Integer, default=0)
    description = Column(String(2000))
    user_mail = Column(String(64), ForeignKey(
        'user.mail', ondelete='CASCADE', onupdate='CASCADE'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            'rating': self.rating,
            'calorie': self.calorie,
            'carb': self.carb,
            'protein': self.protein,
            'fat': self.fat,
            'cooking_minutes': self.cooking_minutes,
            'description': self.description,
            'user_mail': self.user_mail
        }


class Favorite(Base):
    __tablename__ = 'favorite'

    user_mail = Column(String(64), ForeignKey(
        'user.mail', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    user = relationship(User)
    recipe_id = Column(Integer, ForeignKey(
        'recipe.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    recipe = relationship(Recipe)

    @property
    def serialize(self):
        return {
            'recipe_id': self.recipe_id
        }


class Recipe_Food(Base):
    __tablename__ = 'recipe_food'

    food_name = Column(String(64), ForeignKey(
        'food.name', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    food = relationship(Food)
    recipe_id = Column(Integer, ForeignKey(
        'recipe.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    recipe = relationship(Recipe)

    @property
    def serialize(self):
        return {
            'food_name': self.food_name,
            'recipe_id': self.recipe_id
        }

engine = create_engine('mysql+pymysql://{your-username}:{your-password}@{your-ip:port}/{your-database}')
Base.metadata.create_all(engine)
