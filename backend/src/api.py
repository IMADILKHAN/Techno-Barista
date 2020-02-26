import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES
# shows drinks
@app.route('/drinks',methods=['GET'])
def show_drinks():
    drinks = list(map(Drink.short, Drink.query.all()))
    return jsonify({
        'sucess':True,
        'drinks':drinks
    })


# shows the drinks in detail
@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def show_drinks_detail(token):
    drinks = list(map(Drink.long,Drink.query.all()))
    return jsonify({
        'sucess':True,
        'drinks':drinks
    })

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(token):
    if request.data:
        new_drink_data = json.loads(request.data.decode('utf-8'))
        new_drink = Drink(title = new_drink_data['title'], recipe = json.dumps(new_drink_data['recipe']))
        Drink.insert(new_drink)
        drinks = list(map(Drink.long , Drink.query.all()))
        result = jsonify({
            'sucess':True,
            'drinks':drinks
        })
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@app.requires_auth('patch:drinks')
def patch_Drinks(token,drink_id):
    new_drink_data = json.loads(request.data.decode('utf-8'))
    drink_data = Drink.query.get(drink_id)
    if 'title' in new_drink_data:
        setattr(drink_data, 'title', new_drink_data['title'])
    if 'recipe' in new_drink_data:
        setattr(drink_data, 'recipe', new_drink_data['recipe'])
    Drink.update(drink_data)
    drinks = list(map(Drink.long , Drink.query.all()))
    retur jsonify({
        'sucess':True,
        'drinks':drinks
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>' , methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_Drinks(token,drink_id):
    drink = Drink.query.get(drink_id)
    Drink.delete(drink)
    drinks = list(map(Drink.long , Drink.query.all()))

    return jsonify({
        "sucess":True,
        "drinks":drinks
    })
## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
