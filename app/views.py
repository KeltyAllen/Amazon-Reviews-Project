from flask import render_template, _app_ctx_stack, jsonify, request
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db
#import numpy as np
#import matplotlib.pyplot as plt
import MySQLdb
import sys
import simplejson
import numpy as np

import nltk
from nltk.collocations import *
import string
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.porter import *
from Queue import PriorityQueue
import datetime as dt
import time
import heapq
bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()


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
	data = cursor.fetchall()
	if data:
		return data
	else:
		return "error"
	
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
	
	PID = ' ' + product_id
	tablename =  'all_hk'
	query = "Select RTime, RScore, RSummary, RText From " + tablename +" Where PID = "  +'"' + PID +'" ORDER BY RTime ASC;'
	#ptitle?

	#did they input a pid, title, or neither?
	data = query_db(query)
	
	if data == "error":
		print "not a pid"
		#query = "Select PID, PTitle From " + tablename +" Where PTitle Like "  +'"%' + product_id +'%" Limit 11'
		query = "Select PID, PTitle from (SELECT PID, PTitle, COUNT(*) AS magnitude FROM " + tablename + ' Where PTitle like "%' +product_id + '%" GROUP BY PID Order by magnitude desc) as a LIMIT 10;'
		prodlist = query_db(query)
		PID = prodlist[0][0]
		query = "Select RTime, RScore, RSummary, RText From " + tablename +" Where PID = "  +'"' + PID +'" ORDER BY RTime ASC;'
		data = query_db(query)

	formatted_data = map(lambda d: {'time': d[0], 'rating':d[1]}, data)
	add_average_rating(formatted_data)
	
	#Here I do the analysis to get the start of the popular time, and the 3 reviews that explain it some

######### THIS LOOKS LIKE AN UNNECESSARY DB CALL #############
	rating, time = get_data(PID, tablename)
########### CHECK ON THIS WHEN TIME ###################	
	
	popmin, popmax = first_pop_time(time)
	pop_text, pop_revs = get_time_review_text(PID, tablename, popmin, popmax)
	#print pop_text[:200], '\n'
	

	#tot_tokens = get_tokens(tot_text)
	pop_tokens = get_tokens(pop_text)
	
	sql = "Select distinct PTitle from " + tablename +" where PID = " + '"' + PID + '";'
	prodname = query_db(sql)
	#print prodname
	prodname = tuple(x[0] for x in prodname)
	#print prodname
	title = prodname[0]
	prodname = get_tokens(prodname[0])
	#print prodname
	
	finder = BigramCollocationFinder.from_words(pop_tokens)
	finder.apply_freq_filter(4)
	if finder:
		bestbigrams = best_bigram_collector(finder, 5, prodname)

	finder = TrigramCollocationFinder.from_words(pop_tokens)
	#finder.apply_freq_filter(2)
	if finder:
		besttrigrams = best_trigram_collector(finder, 5, prodname)
		
	keywords = [item for sublist in bestbigrams for item in sublist] + [item for sublist in besttrigrams for item in sublist]

	print len(pop_revs)
	count = [0]*len(pop_revs)
	i = 0
	for rev in pop_revs:
		if len(rev)>0:
			for word in get_tokens(rev):
				if word in keywords:
					count[i] += 1
			count[i] = float(count[i])/float(len(rev))
			i += 1
			
	bestrevs = []
	for x, i in enumerate(count):
		if i in heapq.nlargest(3, count):
			bestrevs.append(pop_revs[x])
			
			
	boldrevs = []	
	for rev in bestrevs:
		hold = ''
		for word in rev.split():
			if string.lower(word.translate(None, string.punctuation)) in keywords:
				hold = hold + " <b>"+word + "</b> "
			else:
				hold = hold + ' ' + word + ' '
		if len(hold)<300:
			boldrevs.append(hold)
		else:
			boldrevs.append(hold[:300] + "...")

	charttitle = "Cumulative average reviews for " + title
	#title = '<a href="www.amazon.com/gp/product/'+PID[1:] + '">' + title + '</a>'

	date = dt.datetime.fromtimestamp(popmin)
	poplabel = "This product became frequently reviewed starting <b>" + date.strftime("%B") + " " + str(date.year) + "</b>. " 

	return jsonify(ratings = formatted_data, prodname = title, reviews = boldrevs, title = poplabel)
	
	
	###   
	

@app.route('/times/')
def get_reviews():
	PID = ' ' + request.args['product']
	time1 = request.args['time1']
	time2 = request.args['time2']
	time1 = dt.datetime.strptime(time1, "%Y/%m/%d")
	time2 = dt.datetime.strptime(time2, "%Y/%m/%d")
	print time1, time2
	time1 = time.mktime(time1.timetuple())
	time2 = time.mktime(time2.timetuple())
	
	tablename =  'all_hk'
	query = "Select RTime, RScore, RSummary, RText From " + tablename +" Where PID = "  +'"' + PID +'" ORDER BY RTime ASC;'
	#ptitle?

	#did they input a pid, title, or neither?
	data = query_db(query)
	
	if data == "error":
		print "not a pid"
		#query = "Select PID, PTitle From " + tablename +" Where PTitle Like "  +'"%' + product_id +'%" Limit 11'
		query = "Select PID, PTitle from (SELECT PID, PTitle, COUNT(*) AS magnitude FROM " + tablename + ' Where PTitle like "%' +product_id + '%" GROUP BY PID Order by magnitude desc) as a LIMIT 10;'
		prodlist = query_db(query)
		PID = prodlist[0][0]
		query = "Select RTime, RScore, RSummary, RText From " + tablename +" Where PID = "  +'"' + PID +'" ORDER BY RTime ASC;'
		data = query_db(query)
	
	#rating, times = get_data(PID, tablename)
	pop_text, pop_revs = get_time_review_text(PID, tablename, time1, time2)
	

	pop_tokens = get_tokens(pop_text)	
	
	sql = "Select distinct PTitle from " + tablename +" where PID = " + '"' + PID + '";'
	prodname = query_db(sql)
	#print prodname
	prodname = tuple(x[0] for x in prodname)
	#print prodname
	title = prodname[0]
	prodname = get_tokens(prodname[0])
	
	finder = BigramCollocationFinder.from_words(pop_tokens)
	finder.apply_freq_filter(4)
	if finder:
		bestbigrams = best_bigram_collector(finder, 5, prodname)

	finder = TrigramCollocationFinder.from_words(pop_tokens)
	if finder:
		besttrigrams = best_trigram_collector(finder, 5, prodname)
		
	keywords = [item for sublist in bestbigrams for item in sublist] + [item for sublist in besttrigrams for item in sublist]

	print len(pop_revs)
	count = [0]*len(pop_revs)
	i = 0
	for rev in pop_revs:
		if len(rev)>0:
			for word in get_tokens(rev):
				if word in keywords:
					count[i] += 1
			count[i] = float(count[i])/float(len(rev))
			i += 1
			
	bestrevs = []
	for x, i in enumerate(count):
		if i in heapq.nlargest(3, count):
			bestrevs.append(pop_revs[x])
			
			
	boldrevs = []	
	for rev in bestrevs:
		hold = ''
		for word in rev.split():
			if string.lower(word.translate(None, string.punctuation)) in keywords:
				hold = hold + " <b>"+word + "</b> "
			else:
				hold = hold + ' ' + word + ' '
		if len(hold)<300:
			boldrevs.append(hold)
		else:
			boldrevs.append(hold[:300] + "...")

	charttitle = "Cumulative average reviews for " + title
	#title = '<a href="www.amazon.com/gp/product/'+PID[1:] + '">' + title + '</a>'

	date1 = dt.datetime.fromtimestamp(time1)
	date2 = dt.datetime.fromtimestamp(time2)
	poplabel = "Reviews from <b>" + date1.strftime("%B") + " " + str(date1.year) + "</b> to <b>" + date2.strftime("%B") + " " + str(date2.year) + "</b>. " 

	return jsonify(reviews = boldrevs, title = poplabel)
	


@app.route('/slides')
def about():
    # Renders slides.html.
    return render_template('slides.html')

@app.route('/author')
def contact():
    # Renders author.html.
    return render_template('author.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500



#####################################################
############  Bucket of Functions  ###################
#####################################################


def get_data(PID, tablename):
    sql = "Select RTime, RScore From " +tablename + " Where PID = " + '"' + PID +'";'    
    data = query_db(sql)
    data = sorted(data)
    rating = np.array(zip(*data)[1], dtype = int)
    time = np.array(zip(*data)[0], dtype = float)
    #dates=[dt.datetime.fromtimestamp(ts) for ts in time]
    return rating, time#, dates

def first_pop_time(time): 
    firstpopmin = time[0]
    firstpopmax = time[len(time)-1]
    slidermin = 0
    slidersize = max(int(len(time)/4), 4)
    avtime = (time[len(time)-1] - time[0])/len(time)
    for i in range(slidersize, len(time)): #i marks the end of the slider
        windowsize = time[i] - time[i - slidersize]
        if windowsize < ((time[len(time)-1] - time[0])/4) and (time[i-slidersize]-time[i - slidersize - 3]) < 3*avtime:   
            firstpopmax = time[i]
            firstpopmin = time[i - slidersize]
            break;
    #dates=[dt.datetime.fromtimestamp(ts) for ts in time]
    print dt.datetime.fromtimestamp(firstpopmin), dt.datetime.fromtimestamp(firstpopmax)
    return firstpopmin, firstpopmax
    
    
    # i think this method is super slow
def get_tokens(text):
	lowers = text.lower()
	no_punctuation = lowers.translate(None, string.punctuation)
	tokens = nltk.word_tokenize(no_punctuation)
	filtered = [w for w in tokens if not w in stopwords.words('english')]
	return filtered

def get_tot_review_text(PID, tablename):
    rating, time = get_data(PID, tablename)
    popmin, popmax = first_pop_time(time)
    text = ''
    sql = "Select RSummary From " +tablename + " Where PID = " + '"' + PID +'"' + " and rtime < " + str(popmax) + ";"
    rtext = query_db(sql)
    rtext = tuple(x[0] for x in rtext)
    for string in rtext:
        text = text + string
    sql = "Select RText From " +tablename + " Where PID = " + '"' + PID +'"' + " and rtime < " + str(popmax) + ";"
    rtext = query_db(sql)
    rtext = tuple(x[0] for x in rtext)
    for string in rtext:
        text = text + string
    return text
    
    ####is this method slow?
def get_time_review_text(PID, tablename, timemin, timemax):
    #rating, time = get_data(PID, tablename)
    #popmin, popmax = first_pop_time(time)
    text = ''
    print "getting summaries"
    sql = "Select RSummary From " +tablename + " Where PID = " + '"' + PID +'"' + ' and rtime > ' + str(timemin)+ " and rtime < " + str(timemax) + ";"
    rtext = query_db(sql)
    rtext = tuple(x[0] for x in rtext)
    for string in rtext:
        text = text + string
    sql = "Select RText From " +tablename + " Where PID = " + '"' + PID +'"' + ' and rtime > ' + str(timemin)+ " and rtime < " + str(timemax) + ";"
    rtext = query_db(sql)
    rtext = tuple(x[0] for x in rtext)
    for string in rtext:
        text = text + string
    return text, rtext
    
def best_bigram_collector(finder, n, ptitle):
	prodlist = finder.nbest(bigram_measures.jaccard, n*10)
	#print "in the function: ", ptitle
	ptitle = get_tokens(str(ptitle))
	#prteint ptitle
	ptitle.append("used")
	bests = []
	count = 0
	words = []
	#print prodlist
	#print ptitle
	for item in prodlist:
		if count < n:
			#print item
			#print item[0], item[1]
			if item[0] not in words and item[1] not in words and item[0] not in ptitle and item[1] not in ptitle:
				#print "got through if-statement"
				bests.append(item)
				words.append(item[0])
				words.append(item[1])
				#words.append(item[2])
				count = count + 1
			else:
				words.append(item[0])
				words.append(item[1])
				#words.append(item[2])
		else:
			break;
	return bests   
    
def best_trigram_collector(finder, n, ptitle):
    prodlist = finder.nbest(trigram_measures.raw_freq, n*10)
    #ptitle = get_tokens(str(ptitle))
    ptitle.append("used")
    bests = []
    count = 0
    words = []
    for item in prodlist:
        if count < n:
        	#print item
        	if item[0] not in words and item[1] not in words and item[2] not in words and item[0] not in ptitle and item[1] not in ptitle and item[2] not in ptitle:   
        		bests.append(item)
        		words.append(item[0])
        		words.append(item[1])
        		words.append(item[2])
        		count = count + 1
        	else:
        		words.append(item[0])
          	words.append(item[1])
          	words.append(item[2])
        else:
            break;
    return bests
    
    
    

### do i even need this anymore? 
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed
