from functions import *
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import pymongo

app=Flask(__name__)

# Supporting Cross Origin requests for all APIs
cors = CORS(app)

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Library Management Platform"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

@app.route('/v1/users', methods=['POST'])
def post_user_details():
	inputBody = request.get_json()
	# perform validations on input
	# If any issue --> return 400 with message ({"error_message": ""})
	# If not, go forward.
	# call the appropriate method in functions.py
	# If sucess -> return response with 200
	# If exception -> return exception message as a json string ({"error_message": "There seems to be some internal issue. Please tru after some time."}) with appopriate 500 (Internal Server Error) .. Oops, something went wrong
	response = user(inputBody) # json.dumps convert dict/json object to string AND json.loads convert a string to dict/json object
	return response, 200

@app.route('/v1/users/<string:user_id>', methods=['GET'])
def get_user_details(user_id):
	response = display_userdetails(user_id)
	return response, 200

@app.route('/v1/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
	response = del_user(user_id)
	return response, 200

@app.route('/v1/users/<string:user_id>', methods=['PATCH'])
def update_user_details(user_id):
	inputBody = request.get_json()
	response = update_userdetails(user_id, inputBody)
	return response, 200

@app.route('/v1/books', methods=['POST'])
def add_book_details():
	inputBody = request.get_json()
	response = add_book(inputBody)
	return response, 200

@app.route('/v1/books/<string:Book_id>', methods=['GET'])
def get_book_deatils(Book_id):
	response=display_book(Book_id)
	return response, 200


@app.route('/v1/books', methods=['GET'])
def get_books_onparams():
		
	if 'offset' in request.args:
		offset = int(request.args['offset'])
	else:
		offset = 0

	if 'limit' in request.args:	
		limit = int(request.args['limit'])
	else:
		limit = 10
	
	dict = {}
	if 'title' in request.args:
		dict['title'] = {"$regex" : request.args['title'], '$options' : 'i'}
	if 'authors' in request.args:
		dict['authors'] = {"$regex" : request.args['authors'], '$options' : 'i'}
	
	response = display_all_books(offset, limit, dict)
	return response, 200


@app.route('/v1/books/<string:Book_id>', methods=['DELETE'])
def delete_book(Book_id):
	response = del_book(Book_id)
	return response, 200

@app.route('/v1/requests', methods=['POST'])
def create_user_request():
	request_json = request.get_json()
	response = create_request(request_json)
	return response, 200


@app.route('/v1/requests', methods=['GET'])
def get_user_request():
	dict = {}
	if 'Request_id' in request.args:
		dict['Request_id'] = request.args['Request_id']
	if 'User_Id' in request.args:
		dict['User_Id'] = request.args['User_Id']
	if 'Book_Id' in request.args:
		dict['Book_Id'] = request.args['Book_Id']
	if 'Status' in request.args:
		value = request.args['Status'].split(",")
		if len(value) == 1:
			dict['Status'] = request.args['Status']
		elif len(value) == 2:
			dict['Status'] = {'$in' : [value[0], value[1]]}
	if 'Type' in request.args:
		dict['Type'] = request.args['Type']
	response=get_request_params(dict)
	return response, 200


@app.route('/v1/requests/<string:requestid>', methods=['PATCH'])
def update_user_request(requestid):
	body = request.get_json()
	Type = body['Type']
	response=update_request(requestid, Type)
	return response, 200


@app.route('/v1/books/<string:Book_id>/recommendations', methods=['GET'])
def get_recommended_books(Book_id):
	response = recommend_books(Book_id)
	return response, 200


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80)
	#app.run(debug=True)

    #app.run(host='127.0.0.1',port=8080)
    #app.run(host=conf['host'],port=conf['port'], debug=True)

# http_json_string='''{"UID" : "1", "Name" : "Urvashi", "Zip" : "205001"}'''
# user_id='''{"UID" : "2"}'''
# http_zip='''{"UID" : "2", "Zip" : "19999"}'''
# http_book_details='''{"Book_id" : "4", "B_Name" : "Martian", "Genre" : "Fiction", "Copies" : 2}'''
# http_book_details1='''{"bookID":"1", "title":"Martian", "authors":"Andy Weir" ,"average_rating":"4.56", "isbn":"0439785960", "isbn13":"9780439785969", "language_code":"eng", "# num_pages":"652", "ratings_count":"1944099", "text_reviews_count":"26249"}'''
# http_delete_book='''{"title" : "Martian"}'''
# http_book_id='''{"Book_id" : "2"}'''


