import os
from flask import Flask, request, jsonify, abort, flash
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"/api/*": {'origins': '*'}})
app.secret_key = os.getenv('SECRET_KEY')

db_drop_and_create_all()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods','GET, POST, PATCH, DELETE, OPTIONS')  
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ROUTES

@app.route('/drinks', methods=['GET'])
def retrieve_drinks():

    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
      'success': True,
      'drinks': drinks
    }), 200

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(jwt):

    drinks = Drink.query.all()
    drinks = [drink.long() for drink in drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
      'success': True,
      'drinks': drinks
    }), 200



@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_a_new_drink(jwt):
    error = False
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')

    add_drink = Drink(title=title, recipe=json.dumps(recipe))

    try:
      add_drink.insert()
      flash('Drink ' + str(add_drink.id) + ' was successful listed!')
    except Exception as e:
      print(e)
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Drink ' + str(add_drink.id) + ' could not be listed.')
    finally:
      db.session.close()
      add_drink = [add_drink.long()]
    if error:
      abort(400)
    else:
      return jsonify({
            "success": True,
            "drinks": add_drink
                    }), 200



@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_an_existing_drink(jwt, drink_id):
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')
    try:
        drink = db.session.query(Drink).get(drink_id)
    except Exception as e:
        print(e)
        abort(404)
    try:
        if title == None:
            None
        else:
            drink.title = title
        if recipe == None:
            None
        else:
            drink.recipe = json.dumps(recipe)
        db.session.commit()
    except Exception as e:
        print(e)
        print(422)
    return jsonify({
            "success": True,
            "drinks": [drink.long()]
                    }), 200



@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_an_existing_drink(jwt, drink_id):
    try:
        drink = db.session.query(Drink).get(drink_id)
    except Exception as e:
        print(e)
        abort(404)
    try:
        drink.delete()
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        print(500)
    return jsonify({
            "success": True,
            "delete": drink_id
                    }), 200



# Error Handling


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request, Client Error"
    }), 400

@app.errorhandler(401)
def unauthorized_request(error):
    return jsonify({
      "success": False,
      "error": 401,
      "message": "unauthorized request, please check your permissions"
    }), 401

@app.errorhandler(403)
def request_forbidden(error):
    return jsonify({
      "success": False,
      "error": 403,
      "message": "request is forbidden"
    }), 403

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

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response