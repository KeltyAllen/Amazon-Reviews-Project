from flask import render_template, _app_ctx_stack, jsonify
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db
#import numpy as np
#import matplotlib.pyplot as plt
import MySQLdb
import sys
import simplejson
import numpy as np


# To create a database connection, add the following
# within your view functions:
# con = con_db(host, port, user, passwd, db)

#from app.helpers.database import con_db, query_db
#from app.helpers.filters import format_currency
import jinja2
 
def get_db():
	print "Getting DB"
	top = _app_ctx_stack.top
	if not hasattr(top, 'home_kitchen_db'):
		top.home_kitchen_db = MySQLdb.connect(host="localhost", user="root", db = "home_kitchen")
	return top.home_kitchen_db

def query_db(query):
	sys.stderr.write("Querying Database with: "  + query)
	cursor = get_db().cursor()
	cursor.execute(query)
	return cursor.fetchall()
	
def add_average_rating(data):
	total = 0
	for index, datum in enumerate(data):
		total += datum['rating']
		datum['average_rating'] = total/(index+1)	

@app.route('/')
def index():
	return render_template('index.html')
 
@app.route('/product/json/<product_id>')
def product_details(product_id):  #which table? need to combine them before demo day probably
	query = "Select RTime, RScore From all_hk Where PID = \" " + product_id +'" ORDER BY RTime ASC;'
	data = query_db(query)

	formatted_data = map(lambda d: {'time': d[0], 'rating':d[1]}, data)
	add_average_rating(formatted_data)
	return jsonify(reviews = formatted_data)	


	


