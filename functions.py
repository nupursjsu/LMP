from pymongo import MongoClient
from bson.json_util import dumps
from settings import *
import json
from datetime import datetime
from flask import Flask, jsonify, request
import pymongo

def user(user_details):
    conn = MongoClient(conf['mongo_url'])
    uname = user_details['userId']
    user_details['_id'] = uname
    db=conn.Books
    collection=db.myapp_user
    put=collection.insert_one(user_details)
    return json.dumps({"Success" : "User has been added"})


def display_userdetails(user_id):
    conn = MongoClient(conf['mongo_url'])
    db=conn.Books
    collection=db.myapp_user
    get=collection.find_one({'userId' : user_id}, {'_id' : False})
    mydict=dumps(get)
    conn.close()
    return mydict


def del_user(user_id):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	collection=db.myapp_user
	collection.delete_one({'userId':user_id})
	return json.dumps({"Success" : "User has been deleted"})


def update_userdetails(user_id, user_details):
    conn=MongoClient(conf['mongo_url'])
    db=conn.Books
    collection=db.myapp_user
    collection.update_one({"userId": user_id},
                                 {"$set" : user_details})
    return json.dumps({"Success" : "Details updated"})

def add_book(book_details):
	conn=MongoClient(conf['mongo_url'])
	book_id = book_details['bookID']
	book_details['_id'] = book_id
	db=conn.Books
	coll=db.library_books_new
	put=coll.insert_one(book_details)
	return json.dumps({"Success" : "Book has been added"})


def del_book(book_id):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.library_books_new
	coll.delete_one({'bookID' : book_id})
	return json.dumps({"Success" : "Book has been deleted"})

def display_book(book_id):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.library_books_new
	get=coll.find_one({'bookID' : book_id},{'_id' : False})
	mydict=dumps(get)
	return mydict

def display_all_books(offset, limit):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.library_books_new
	books = coll.find({}, {'_id' : False}).skip(offset).sort('bookID', pymongo.ASCENDING).limit(limit)
	output = []
	for i in books:
		output.append({'title': i['title'], 'bookID' : i['bookID'], 'isbn' :i['isbn'], 'authors' : i['authors'], 'year' : i['year'], 'publisher' : i['publisher'], 'average_rating' : i['average_rating']})

	next_url = '/v1/books?limit=' + str(limit) + '&offset=' + str(offset + limit)
	prev_url = '/v1/books?limit=' + str(limit) + '&offset=' + str(offset - limit)
	
	return jsonify({'result' : output, 'prev_url' : prev_url, 'next_url' : next_url})
	
# def display_all_books():
# 	conn=MongoClient(conf['mongo_url'])
# 	db=conn.Books
# 	coll=db.library_books_new
# 	get = coll.find({}, {'_id' : False})
# 	mydict=dumps(get)
# 	return mydict


def display_book_onparams(dict):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.library_books_new
	get=coll.find(dict, {'_id' : False})
	mydict=dumps(get)
	return mydict

def book_action_taken(user_id, book_id, action_taken):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.Request
	request_id = user_id + "-" +book_id
	if action_taken['action']=='issue':
		data = { "_id" : request_id, 
		"Request_id": request_id,
		"User_Id" : user_id, 
		"Book_Id" : book_id, 
		"Type" : "issue", 
		"Status" : "Pending", 
		"request_time" :  datetime.now()
		}
		coll.insert_one(data)

	if action_taken['action']== 'return':
		coll.update_one({'Request_id' : request_id}, {'$set' : {'Type' : 'return', 'Status' : 'Pending'}})
	
	if action_taken['action'] == 're-issue':
		coll.update_one({'User_Id':user_id}, {'Book_Id' : book_id}, {'$set' : {'Type' : 're-issue', 'Status' : 'Pending'}})

	
	url=conf['host_url'] + "/v1/requests/" + request_id
	response = json.dumps({"Status_Url" : url})
	return response

def request_details(request_id):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.Request
	get=coll.find_one({'Request_id':request_id})
	mydict=dumps(get)
	return mydict

def all_requests():
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.Request
	get=coll.find({},{'_id' : False})
	mydict=dumps(get)
	return mydict

def get_request_params(dict):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.Request
	get=coll.find(dict, {'_id': False})
	mydict=dumps(get)
	return mydict





# def reduce_book(http_book_id):

# 	bid=json.loads(http_book_id)
# 	conn=MongoClient(conf['mongo_url'])
# 	db=conn.Books
# 	coll=db.library_books_new
# 	coll.update_one(bid, {"$inc" : {"Copies" : 1}})

# GET /v1/books/<bookId>

# GET /v1/books?title=<title>&author=<title>&start=50&end=100&q=
# We will need a TextIndex for a full text search in MongoDB (q)
# https://stackoverflow.com/questions/6790819/searching-for-value-of-any-field-in-mongodb-without-explicitly-naming-it
# title = request.args.get('title')
# { 
#	"start": 0,
#   "end": 50,
#   "params": "",
#   "books": [{}]
# }
# db.students.find().skip((pageNumber-1)*nPerPage).limit(nPerPage).forEach( function(student) { print(student.name + "<p>"); } );
# output = dict()
# output["start"] = 0
# output["end"] = 50
# output["params"] = ""
# output["books"] = mydict
# return output
# @app.route('/v1/books/<search>/', methods=['GET']) #http://127.0.0.1:5000/v1/books/%5EHarry.*/
# def find_book(search):
# 	print(search)
# 	conn=MongoClient(conf['mongo_url'])
# 	db=conn.Books
# 	coll=db.library_books_new
# 	get=coll.find({"title" : {"$regex": search}}, {'_id' : False})
# 	print(get)
# 	mydict=dumps(get)
# 	conn.close()
# 	return mydict


