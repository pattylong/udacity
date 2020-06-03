import os
from flask import Flask, request, jsonify, abort, render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from sqlalchemy import exc
import json
from flask_cors import CORS
from datetime import datetime

#from auth.auth import AuthError, requires_auth
from functools import wraps

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User, Recipe, Tag, db


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


"""
###############################################################
#########################   ROUTES   ##########################
###############################################################
"""


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def home():
    #return "hello"
    return render_template('index.html')


@app.route('/users', methods=['GET'])
@login_required
def get_all_users():
    data = []
    users = db.session.query(User.id, User.name).all()
    if not users:
        return "There are currently no users."
    for user in users:
        data.append({
            "id": user.id,
            "name": user.name
        })

    result = {"data": data,
              "success": True}

    return jsonify(result)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.name)
    if form.validate_on_submit():
        current_user.name = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(name=username).first_or_404()
    recipes = [
        {'user': user, 'body': 'Mac and Cheese'},
        {'user': user, 'body': 'Burger and Fries'}
    ]
    return render_template('user.html', user=user, recipes=recipes)


@app.route('/users', methods=['POST'])
def add_user():
    return None


@app.route('/recipes', methods=['GET'])
def get_all_recipes():
    data = []
    recipes = db.session.query(Recipe).order_by(Recipe.name).all()
    if not recipes:
        return "You currently have no recipes."
    for recipe in recipes:
        data.append({
            "id": recipe.id,
            "user_id": recipe.user_id,
            "name": recipe.name,
            "tags": recipe.tag
        })

    result = {"data": data,
              "success": True}

    return jsonify(result)


@app.route('/tags', methods=['GET'])
def get_all_tags():
    data = []
    tags = db.session.query(Tag).order_by(Tag.name).all()
    if not tags:
        abort(404)
    for tag in tags:
        data.append({
            "id": tag.id,
            "name": tag.name
        })

    result = {"data": data,
              "success": True}

    return jsonify(result)


@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe_with_id(recipe_id):
    recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
    if not recipe:
        abort(404)
    data = {
        "id": recipe.id,
        "user_id": recipe.user_id,
        "name": recipe.name,
        "instructions": recipe.instructions,
        "ingredients": recipe.ingredients,
        "recipe_link": recipe.recipe_link,
        "tags": recipe.tags
    }

    result = {"data": data,
              "success": True}

    return jsonify(result)


@app.route('/users/<int:user_id>/recipes', methods=['GET'])
def get_user_recipes(user_id):
    recipes = db.session.query(User.recipes).filter_by(id=user_id).all()
    if not recipes:
        abort(404)
    data = []
    for recipe in recipes:
        data.append({
            "id": recipe.id,
            "user_id": recipe.user_id,
            "name": recipe.name,
            "tags": recipe.tags
        })

    result = {"data": data,
              "success": True}

    return jsonify(result)


@app.route('/tags/<int:tag_id>/recipes', methods=['GET'])
def get_tag_recipes(tag_id):
    recipes = db.session.query(Tag.recipes).filter_by(id=tag_id).all()
    if not recipes:
        abort(404)
    data = []
    for recipe in recipes:
        data.append({
            "id": recipe.id,
            "user_id": recipe.user_id,
            "name": recipe.name,
            "tags": recipe.tags
        })

    result = {"data": data,
              "success": True}

    return jsonify(result)





