import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(422)

        result = {'success': True,
                  'categories': {category.id: category.type for category in categories}}

        return jsonify(result)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', default=1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        all_questions = Question.query.all()
        categories = Category.query.all()
        questions = all_questions[start:end]

        if len(questions) == 0:
            abort(404)

        questions_formatted = [q.format() for q in questions]

        result = {'success': True,
                  'questions': questions_formatted,
                  'total_questions': len(all_questions),
                  'categories': {category.id: category.type for category in categories},
                  'current_category': None
                  }

        return jsonify(result)

    @app.route('/questions/<int:qid>/delete', methods=['DELETE'])
    def remove_question(qid):
        q = Question.query.filter(Question.id == qid).one()

        if q is None:
            abort(404)

        db.session.delete(q)
        db.session.commit()

        result = {'success': True,
                  'deleted': qid}

        return jsonify(result)

    @app.route('/add', methods=['POST'])
    def create_question():
        data = request.json

        question = Question(question=data['question'], answer=data['answer'],
                            category=data['category'], difficulty=data['difficulty'])

        db.session.add(question)
        db.session.commit()

        result = {'success': True}

        return jsonify(result)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search_term = request.json['searchTerm']
        search_term_adj = '%{0}%'.format(search_term)
        questions_like_search = Question.query.filter(
            Question.question.ilike(search_term_adj)).all()
        qs_like_search_formatted = [q.format() for q in questions_like_search]

        result = {'success': True,
                  'questions': qs_like_search_formatted,
                  'total_questions': len(qs_like_search_formatted),
                  'current_category': None}

        return jsonify(result)

    @app.route('/categories/<int:cid>/questions', methods=['GET'])
    def get_category(cid):
        questions = Question.query.filter(Question.category == cid).all()

        if len(questions) == 0:
            abort(404)

        questions_formatted = [q.format() for q in questions]

        result = {'success': True,
                  'questions': questions_formatted,
                  'total_questions': len(questions_formatted),
                  'current_category': cid}

        return jsonify(result)

    @app.route('/play', methods=['POST'])
    def play_trivia():
        prev_questions = request.json['previous_questions']
        category = request.json['quiz_category']

        # if category is All
        if category['id'] == 0:
            question = Question.query.filter(
                    Question.id.notin_(prev_questions)).order_by(func.random()).first()
        else:
            question = Question.query.filter(
                Question.category == category['id']).filter(
                Question.id.notin_(prev_questions)).order_by(func.random()).first()

        if question is None:
            result = {'success': True,
                      'question': question}
        else:
            result = {'success': True,
                      'question': question.format()}

        return jsonify(result)

    @app.errorhandler(404)
    def not_found(error):
        result = {'success': False,
                  'error': 404,
                  'message': "Resource not found."}

        return jsonify(result), 404

    @app.errorhandler(422)
    def unprocessable(error):
        result = {'success': False,
                  'error': 422,
                  'message': "Unprocessable request."}

        return jsonify(result), 422

    @app.errorhandler(400)
    def bad_request(error):
        result = {'success': False,
                  'error': 400,
                  'message': "Bad request."}

        return jsonify(result), 400

    return app
