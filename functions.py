from pymongo import MongoClient
from bson.json_util import dumps
import json
from datetime import datetime
from flask import Flask, jsonify, request, send_file
import pymongo
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import uuid

def user(user_details, conf):
    conn = MongoClient(conf['mongo_url'])
    uname = user_details['userId']
    user_details['_id']=uname
    if 'is_admin' not in user_details:
    	user_details['is_admin'] = "No"
    db=conn.Books
    coll=db.myapp_user
    if coll.find({'userId': uname}).count() > 0:
    	return json.dumps({"Authenticated" : "User already present"})
    else:
    	coll.insert_one(user_details)
    	return json.dumps({"Registered" : "New user has been added"})


def display_userdetails(user_id, conf):
    conn = MongoClient(conf['mongo_url'])
    db=conn.Books
    collection=db.myapp_user
    get=collection.find_one({'userId' : user_id}, {'_id' : False})
    mydict=dumps(get)

    conn.close()
    return mydict


def del_user(user_id, conf):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	collection=db.myapp_user
	collection.delete_one({'userId':user_id})
	return json.dumps({"Success" : "User has been deleted"})


def update_userdetails(user_id, user_details, conf):
    conn=MongoClient(conf['mongo_url'])
    db=conn.Books
    collection=db.myapp_user
    collection.update_one({"userId": user_id},
                                 {"$set" : user_details})
    return json.dumps({"Success" : "Details updated"})

def del_user(user_id, conf):
	conn=MongoClient(conf['mongo_url'])
	book_id = book_details['bookID']
	book_details['_id'] = book_id
	db=conn.Books
	coll=db.library_books_new
	put=coll.insert_one(book_details)
	return json.dumps({"Success" : "Book has been added"})


def del_book(book_id, conf):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.library_books_new
	coll.delete_one({'bookID' : book_id})
	return json.dumps({"Success" : "Book has been deleted"})

def display_book(book_id, conf):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.library_books_new
	get=coll.find_one({'bookID' : book_id},{'_id' : False})
	mydict=dumps(get)
	return mydict

def display_all_books(offset, limit, dict, conf):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.library_books_new
	get = coll.find(dict, {'_id' : False}).sort('_id', pymongo.ASCENDING).skip(offset).limit(limit)
	mydict=dumps(get)
	return mydict

def create_request(request_json, conf):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.Request
	coll2=db.library_books_new
	request_id = str(uuid.uuid1())
	book_id = request_json['bookID']
	user_id = request_json['userId']
	title = request_json['title']
	if request_json['Type']=='issue':
		data = { "_id" : request_id, 
		"Request_id": request_id,
		"User_Id" : user_id, 
		"Book_Id" : book_id, 
		"title" : title,
		"Type" : "issue", 
		"Status" : "Approved", 
		"request_time" :  datetime.now()
		}
		coll.insert_one(data)
		coll2.update_one({'bookID' : book_id}, {'$inc' : {'count' : -1}})

	url=conf['host_url'] + "/v1/requests/" + request_id
	response = json.dumps({"Status_Url" : url})
	return response

# request_id and Type mandatory
def update_request(request_id, Type, conf):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.Request
	coll2=db.library_books_new

	if (Type == 'reissue'):
		document = dict(coll.find_one({'Request_id':request_id},{'request_time' : 1, 'issue_time' : 1, '_id' : False}))
		document['re-issue_time'] = datetime.now()
		coll.update({'Request_id':request_id}, {'$set' : {'Type' : 'reissue', 'request_time' : datetime.now(), 'issue_time' : datetime.now()}, '$push' : {'history' : document	}})
		return json.dumps({"Success" : "Book has been re-issued"})

	elif (Type == 'return'):
		coll.update({'Request_id':request_id}, {'$set' : {'Status' : 'Returned', 'return_time' :  datetime.now()}})
		document = dict(coll.find_one({'Request_id':request_id},{'Book_Id' : 1, '_id' : False }))
		document['bookID'] = document['Book_Id']
		document.pop("Book_Id")
		coll2.update(document, {'$inc' : {'count' : 1}})
		return json.dumps({"Success" : "Book has been returned"})

	elif (Type == 'issue'):
		coll.update({'Request_id':request_id}, {'$set' : {'Status' : 'Issued', 'issue_time' : datetime.now()}})
		return json.dumps({"Success" : "Book has been issued"})



def get_request_params(dict, conf):
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.Request
	get=coll.find(dict, {'_id': False})
	mydict=dumps(get)
	return mydict


def recommend_books(book_id, conf):

	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.library_books_new

	books = pd.read_csv('userRatings.csv')

	#create a pivot table 
	books_pivot = books.pivot(index='bookTitle', columns = 'userID', values = 'bookRating').fillna(0)
	books_matrix = csr_matrix(books_pivot.values)
	model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
	model_knn.fit(books_matrix)

	query_index = int(book_id)
	distances, indices = model_knn.kneighbors(books_pivot.iloc[query_index,:].values.reshape(1,-1),n_neighbors=6)
	l = []
	for i in range(0,len(distances.flatten())):
		if i != 0:
			l.append(indices.flatten()[i])

	output = []
	for j in l:
		get = coll.find({'bookID' : str(j)}, {'_id' : False})
		for i in get:
			output.append(i)
	return jsonify({'result' : output})


# def check_authorization(token_id, user_id):
# 	decoded_token = auth.verify_id_token(id_token)
# 	uid = decoded_token['uid']
# 	if uid == user_id:
# 		return 200
# 	else:
# 		return 400


# check_authorization()




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


