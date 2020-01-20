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

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    # CORS Headers
    @app.after_request
    def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response


    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
      categories = Category.query.all()

      if len(categories) == 0:
        abort(422)

      result = {'success': True,
                'categories': {category.id: category.type for category in categories}}

      return jsonify(result)

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
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


    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
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


    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''

    @app.route('/add', methods=['POST'])
    def create_question():
      data = request.json

      question = Question(question=data['question'], answer=data['answer'],
                          category=data['category'], difficulty=data['difficulty'])

      db.session.add(question)
      db.session.commit()

      result = {'success': True}

      return jsonify(result)


    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
      search_term = request.json['searchTerm']
      search_term_adj = '%{0}%'.format(search_term)
      questions_like_search = Question.query.filter(Question.question.ilike(search_term_adj)).all()
      qs_like_search_formatted = [q.format() for q in questions_like_search]

      result = {'success': True,
                'questions': qs_like_search_formatted,
                'total_questions': len(qs_like_search_formatted),
                'current_category': None}

      return jsonify(result)

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
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


    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/play', methods=['POST'])
    def play_trivia():
      prev_questions = request.json['previous_questions']
      category = request.json['quiz_category']

      question = Question.query.filter(
                                Question.category == category['id']).filter(
                                Question.id.notin_(prev_questions)).order_by(func.random()).first()

      result = {'success': True,
                'question': question.format()}

      return jsonify(result)


    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found():
      result = {'success': False,
                'error': 404,
                'message': "Resource not found."}

      return jsonify(result), 404


    @app.errorhandler(422)
    def not_found():
      result = {'success': False,
                'error': 422,
                'message': "Unprocessable request."}

      return jsonify(result), 422

    return app