import os
from sqlalchemy import Column, String, Integer, ForeignKey, Table, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app import db
from flask import Flask
import json


Base = declarative_base()


'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple verisons of a database
'''


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


# ------------- RELATIONSHIP TABLES -----------

recipeTags = Table('recipeTag', Base.metadata,
                   Column('recipe_id', Integer, ForeignKey('recipe.id'), primary_key=True),
                   Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True)
                   )


# ------------- MODELS -----------

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)
    recipes = db.relationship('Recipe', backref='user', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.name)


class Recipe(Base):
    __tablename__ = 'recipe'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(String(100), nullable=False)
    instructions = Column(String)
    ingredients = Column(String)
    recipe_link = Column(String)
    tags = relationship('Tag', secondary=recipeTags, lazy='subquery',
                         backref=db.backref('recipes', lazy=True))


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)


"""

class Ingredient(Model):
    __tablename__ = 'ingredient'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)


class IngredientQuantity(Model):
    __tablename__ = 'ingredientQuantity'
    id = Column(Integer, primary_key = True)

"""







