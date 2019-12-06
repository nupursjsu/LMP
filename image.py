import urllib.request
from pymongo import MongoClient
from bson.json_util import dumps
from settings import *
import json
from datetime import datetime
from flask import Flask, jsonify, request
import pymongo
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import uuid


# def download_image(): 
# 	conn = MongoClient(conf['mongo_url'])
# 	db=conn.Books
# 	coll=db.library_books_new
# 	get = coll.find({},{'_id' : False})
# 	for i in get:
# 		urllib.request.urlretrieve(i['image'], "images/{}.jpg".format(i['bookID']))

# download_image()


def update_book():
	conn=MongoClient(conf['mongo_url'])
	db=conn.Books
	coll=db.library_books_new
	get = coll.find({},{'_id' : False})
	for i in get:
		path = "https://lmp.nupursjsu.net/v1/images/{}".format(i['bookID'])
		coll.update_one({"bookID": i['bookID']},
                                 {"$set" : {'image' : path}})

	return json.dumps({"Success" : "Image has been updated"})

print(update_book())
