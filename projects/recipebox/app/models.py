import os
from sqlalchemy import Column, String, Integer, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from app import db
from app import login
from hashlib import md5
from flask import Flask
from datetime import datetime
import json


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


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

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )

# ------------- MODELS -----------

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(30), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    recipes = db.relationship('Recipe', backref='user', lazy=True)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
                digest, size)


class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('user.id'), nullable=False)
    name = db.Column(String(100), nullable=False)
    created_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
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







