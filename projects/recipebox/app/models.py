import os
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app import db
from flask import Flask
import json




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

recipeTags = db.Table('recipeTags',
                   db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
                   db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                   )


# ------------- MODELS -----------

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(30), unique=True, nullable=False)
    recipes = db.relationship('Recipe', backref='user', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.name)


class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('user.id'), nullable=False)
    name = db.Column(String(100), nullable=False)
    instructions = db.Column(String)
    ingredients = db.Column(String)
    recipe_link = db.Column(String)
    tags = db.relationship('Tag', secondary=recipeTags, lazy='subquery',
                         backref=db.backref('recipes', lazy=True))


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(50), unique=True, nullable=False)


"""

class Ingredient(Model):
    __tablename__ = 'ingredient'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)


class IngredientQuantity(Model):
    __tablename__ = 'ingredientQuantity'
    id = Column(Integer, primary_key = True)

"""







