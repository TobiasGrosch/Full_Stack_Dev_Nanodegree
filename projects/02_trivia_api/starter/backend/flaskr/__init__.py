import os
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
from dotenv import load_dotenv
from pathlib import Path
import random
import sys

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"/api/*": {'origins': '*'}})
  app.secret_key = os.getenv('SECRET_KEY')

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods','GET, POST, DELETE, OPTIONS')  
    return response

  @app.route('/categories', methods=['GET'])
  def retrieve_categories():

    categories = Category.query.all()
    formatted_categories = {}
    for category in categories:
      formatted_categories[category.id] = category.type

    return jsonify({
      'success': True,
      'categories': formatted_categories
    })

  @app.route('/questions', methods=['GET'])
  def retrieve_questions_page():

    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    categories = Category.query.all()
    formatted_categories = {}
    for category in categories:
      formatted_categories[category.id] = category.type

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': formatted_categories,
      'current_category': None
    })
  
  @app.route('/questions', methods=['POST'])
  def post_a_new_questions():

    error = False
    body = request.get_json()
    #print(body)
    question = body.get('question')
    answer = body.get('answer')
    difficulty = body.get('difficulty')
    category = body.get('category')

    entire_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)

    try:
      entire_question.insert()
      flash('Question ' + str(entire_question.id) + ' was successful listed!')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Question ' + str(entire_question.id) + ' could not be listed.')
    finally:
      db.session.close()
    if error:
      abort(400)
    else:
      return jsonify({
        'success': True,
        'question': question,
        'answer': answer,
        'difficulty': difficulty,
        'category': category
      })

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    error = False
    try:
      question = Question.query.get(question_id)
      question.delete()
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if error:
      abort(404)
    else:
      return jsonify({
        'success': True,
        'deleted': question_id
        })
    return None

  @app.route('/questions/search', methods=['POST'])
  def search_for_questions():
    
    body = request.get_json()
    search_term = body.get('searchTerm')
    response = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
    current_responses = paginate_questions(request, response)

    return jsonify({
      "success": True,
      "questions": current_responses,
      "total_questions": len(Question.query.all()),
      "current_category": None
    })

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def retrieve_questions_based_on_categoy(category_id):

    selection = Question.query.filter(Question.category == category_id).all()
    current_questions = paginate_questions(request, selection)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current_category': category_id
    })

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    try:
      body = request.get_json()
      previous_questions = body.get("previous_questions", [])
      quiz_category = body.get("quiz_category", None)
      category_id = int(quiz_category["id"])
      if quiz_category:
          if quiz_category["id"] == 0:
              quiz = Question.query.all()
          else:
              quiz = Question.query.filter_by(category=category_id).all()
      if not quiz:
          return abort(422)
      selected = []
      for question in quiz:
          if question.id not in previous_questions:
              selected.append(question.format())
      if len(selected) != 0:
          result = random.choice(selected)
          return jsonify({"success": True, "question": result})
      else:
          return jsonify({"success": True, "question": False})
    except:
        abort(422)

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request, Client Error"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found, Client error"
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "request unprocessable"
    }), 422
  
  return app

    