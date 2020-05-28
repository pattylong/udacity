import os
from flask import Flask, request, jsonify, abort, render_template, flash, redirect, url_for
from sqlalchemy import exc
import json
from flask_cors import CORS

#from auth.auth import AuthError, requires_auth
from functools import wraps

from app import app
from app.forms import LoginForm
from app.models import User, Recipe, Tag, db


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


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


"""
###############################################################
#####################   Error Handling   ######################
###############################################################
"""

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def not_found(error):
    app.logger.error('Page not found: %s', request.path)
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                    }), 401


@app.errorhandler(423)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 423,
                    "message": "duplicative"
                    }), 423



