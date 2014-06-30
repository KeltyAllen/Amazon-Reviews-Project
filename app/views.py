from flask import render_template, _app_ctx_stack, jsonify, request
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db
import MySQLdb
import sys
import json
import numpy as np
from urllib2 import Request, urlopen, URLError
import urllib


#from eventlet.timeout import Timeout, with_timeout

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
		
def query_isura_db(address):
	try:
		#response = with_timeout(2, urlopen, address, timeout_value="")
		response = urlopen(address, None, 4)
		answer = response.read()
		return answer
	except:
		return "error"
		

###############################################################################################
		
@app.route('/')
def index():
	return render_template('index.html')


###############################################################################################

@app.route('/times/')
def get_reviews():

	product = request.args['product']
	PID = ' ' + request.args['product']
	time1 = request.args['time1']
	time2 = request.args['time2']
	time1 = dt.datetime.strptime(time1, "%Y/%m/%d")
	time2 = dt.datetime.strptime(time2, "%Y/%m/%d")
	print time1, time2
	time1 = time.mktime(time1.timetuple())
	time2 = time.mktime(time2.timetuple())

	#query isura's db?
	htmlstring =  'http://54.183.117.174:5000/api/v0.2/reviews/' + urllib.quote(product)
	print htmlstring
	answer= query_isura_db(htmlstring)
	
	#answer = "error"
	
	if (answer == "error"):
		#### querying my rds home & kitchen database
		tablename =  'all_hk'
		query = "Select PID, PTitle from (SELECT PID, PTitle, COUNT(*) AS magnitude FROM " + tablename + " Where PTitle like '" +PID + "%' GROUP BY PID Order by magnitude desc) as a LIMIT 10;"
		prodlist = query_db(query)
		PID = prodlist[0][0]
		title = prodlist[0][1]
		query = "Select RTime, RScore, RSummary, RText From " + tablename +" Where PID = "  +'"' + PID +'" ORDER BY RTime ASC;'
		data = query_db(query)
		boldrevs, poplabel = home_kitchen_time(data, title, time1, time2)	
	else:
		jsondata = json.loads(answer)
		###now need to get data, which has data[0] is time list, data[1] is scores, data[2] isn't used anymore (userid?), data[3] is text
		#print jsondata
		reviews = jsondata['reviews']
		data = []
		for i in range(len(reviews)):
			text = reviews[i]['text']
			data.append([reviews[i]['timestamp'], reviews[i]['score'], reviews[i]['userId'], text])
		#print data
		title = product
		boldrevs, poplabel = home_kitchen_time(data, title, time1, time2)

	#boldrevs, poplabel = home_kitchen_time(PID, time1, time2)
	return jsonify(reviews = boldrevs, title = poplabel)
	

###############################################################################################
 
@app.route('/product/json/<product_id>')
def product_details(product_id):  #which table? need to combine them before demo day probably
	
	#Isura's database is up! Woo!
	#Hmm. Often not up. Or super slow? 
	#The following code will get the data as a json file from isura's db, or catch an error if db is down
	#
	#keep this code:
	htmlstring =  'http://54.183.117.174:5000/api/v0.2/reviews/' + urllib.quote(product_id)
	print htmlstring
	answer= query_isura_db(htmlstring)
	#keep this code ^
	
	

	#to only use my database: 
	#answer = "error"
	
	if (answer == "error"):
		#### querying my rds home & kitchen database
		tablename =  'all_hk'
		query = "Select PID, PTitle from (SELECT PID, PTitle, COUNT(*) AS magnitude FROM " + tablename + " Where PTitle like ' " +product_id + "%' GROUP BY PID Order by magnitude desc) as a LIMIT 10;"
		prodlist = query_db(query)
		try:
			PID = prodlist[0][0]
			title = prodlist[0][1]
			query = "Select RTime, RScore, RSummary, RText From " + tablename +" Where PID = "  +'"' + PID +'" ORDER BY RTime ASC;'
			data = query_db(query)
			formatted_data, title, boldrevs, poplabel = home_kitchen_data(data, title)
		except IndexError:
			poplabel = "Sorry! Could not find anything matching " + PID
			formatted_data = []
			title = 'Sorry! Could not find anything matching '+ PID
			boldrevs = []
	else:
		#print answer
		jsondata = json.loads(answer)
		###now need to get data, which has data[0] is time list, data[1] is scores, data[2] isn't used anymore (userid?), data[3] is text
		#print jsondata
		reviews = jsondata['reviews']
		data = []
		for i in range(len(reviews)):
			text = reviews[i]['text']
			data.append([reviews[i]['timestamp'], reviews[i]['score'], reviews[i]['userId'], text])
		#print data
		title = product_id
		formatted_data, title, boldrevs, poplabel = home_kitchen_data(data, title)
			
			
	return jsonify(ratings = formatted_data, prodname = title, reviews = boldrevs, title = poplabel)
	
	

###############################################################################################	
	
@app.route('/slides')
def about():
    # Renders slides.html.
    return render_template('slides.html')  # Renders slides.html.

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

@app.route('/robots.txt')
def static_from_root():
      return send_from_directory(app.static_folder, request.path[1:])
      

###############################################################################################
############  Bucket of Functions  #############################################################
###############################################################################################
			
	
	
	
def get_time_review_text(data, timemin, timemax):
    #rating, time = get_data(PID, tablename)
    #popmin, popmax = first_pop_time(time)
    text = ''
    rtext = np.array(zip(*data)[3])
    times = np.array(zip(*data)[0], dtype = float)
    minindex = 0
    maxindex = len(data)-1

    timemin = float(timemin)
    timemax = float(timemax)
    print "comparing to ", timemin, timemax
    #gets index of first time above timemin as min index
    #gets first index below timemax as max index
    for i in range(len(times)):
        if times[i]<timemin:
            #print i
            minindex = i+1
        if times[i] <= timemax:
            #print i
            maxindex = i
    returntext = []   
    print "minindex, maxindex are ", minindex, maxindex
    
    ###### limit to 200 reviews after min time
    #### either adjust time input at website or remove this if isura's db is miraculously fast
    if maxindex - minindex > 200:
    	maxindex = minindex + 200
    
    for i in range(minindex, maxindex):
        returntext.append(str(rtext[i]))
    for string in returntext:
        text = text + string
    print len(returntext)   
    return text, returntext	
	
	
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
	
def get_tokens(text):
	lowers = text.lower()
	no_punctuation = lowers.translate(None, string.punctuation)
	#super mysterious, it insists translate only takes one argument? it worked fine before?
	#no_punctuation = lowers.translate(None, string.punctuation)
	tokens = nltk.word_tokenize(no_punctuation)
	filtered = [w for w in tokens if not w in stopwords.words('english')]
	filtered = [w for w in filtered if not w in ['used', 'use', 'easy', 'product']]
	return filtered
	
	
def best_bigram_collector(finder, n, ptitle):
	prodlist = finder.nbest(bigram_measures.jaccard, n*10)
	#print "in the function: ", ptitle
	ptitle = get_tokens(str(ptitle))
	#prteint ptitle
	#ptitle.append("used")
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
    ptitle = get_tokens(str(ptitle))
    #ptitle.append("used")
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
    
def add_average_rating(data):
	total = 0
	for index, datum in enumerate(data):
		total += datum['rating']
		datum['average_rating'] = total/(index+1)   
    

### do i even need this anymore? 
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed
	

###############################################################################################
	
##### These used to be main @app.route things, like ('/product/json/<product_id>')and the time one. 
##### The main calculations happen here. 
###### Lots of redundancy between these two functions, clean them up. 

def home_kitchen_data(data, title):
	
    
    
  ## gets time, rating, average rating in a dict
	formatted_data = map(lambda d: {'time': d[0], 'rating':d[1]}, data)
	add_average_rating(formatted_data)
	
	rating = np.array(zip(*data)[1], dtype = int)
	time = np.array(zip(*data)[0], dtype = float)

	popmin, popmax = first_pop_time(time)
	print popmin, popmax

	pop_text, pop_revs = get_time_review_text(data, popmin, popmax)

	print len(pop_revs), len(data)
	print "pop_revs", pop_revs[:5], "\n"

	#pop_text = str(pop_text)
	#print "pop_text", pop_text[:400]
	
	print "tokenizing"
	pop_tokens = get_tokens(str(pop_text))
	
	print "finder = bigramcollocationfinder"
	finder = BigramCollocationFinder.from_words(pop_tokens)
	print "finder.apply_freq"
	finder.apply_freq_filter(4)
	
	
	if finder:
		print "bestbigrams"
		bestbigrams = best_bigram_collector(finder, 5, title)

	print "trigramcoll"
	finder = TrigramCollocationFinder.from_words(pop_tokens)


	if finder:
		print "besttrigrams"
		besttrigrams = best_trigram_collector(finder, 5, title)
	
	print bestbigrams, besttrigrams
	
	keywords = [item for sublist in bestbigrams for item in sublist] + [item for sublist in besttrigrams for item in sublist]

	print len(pop_revs)
	count = [0]*len(pop_revs)
	i = 0
	for rev in pop_revs:
		if len(rev)>0:
			for word in get_tokens(str(rev)):
				if word in keywords:
					count[i] += 1
			count[i] = float(count[i])/float(len(rev))
			i += 1
	
	print "line 392"
	bestrevs = []
	for x, i in enumerate(count):
		if i in heapq.nlargest(3, count):
			bestrevs.append(pop_revs[x])
	
	print "line 398"
	boldrevs = []
	for rev in bestrevs:
		hold = ''
		for word in rev.split():
			if string.lower(word.translate(None, string.punctuation)) in keywords:
				hold = hold + " <strong>"+word + "</strong> "
			else:
				hold = hold + ' ' + word + ' '
		if len(hold)<300:
			boldrevs.append(hold)
		else:
			boldrevs.append(hold[:300] + "...")

	charttitle = "Cumulative average reviews for " + title
#title = '<a href="www.amazon.com/gp/product/'+PID[1:] + '">' + title + '</a>'

	date = dt.datetime.fromtimestamp(popmin)
	poplabel = "This product became frequently reviewed starting <strong>" + date.strftime("%B") + " " + str(date.year) + "</strong>. " 
	
	#Used to do a "did you mean", but no longer do
	
	#if titleflag == 1:
		#if len(prodlist) > 1:
			#suggestions = "Or did you mean " + prodlist[1][1] + " (PID: " + prodlist[1][0]
			#for i in range(2, min(len(prodlist), 4)):
				#suggestions = suggestions + ") or " + prodlist[i][1] + " (PID: " + prodlist[i][0] 
			#poplabel = suggestions +")?" + "<br><br>" + poplabel	
			
	return formatted_data, title, boldrevs, poplabel
	

###############################################################################################
	
def home_kitchen_time(data, title, time1, time2):
	

	#print title
    
	#formatted_data = map(lambda d: {'time': d[0], 'rating':d[1]}, data)
	#add_average_rating(formatted_data)
	
	#rating = np.array(zip(*data)[1], dtype = int)
	#time = np.array(zip(*data)[0], dtype = float)
	
	pop_text, pop_revs = get_time_review_text(data, time1, time2)
	print len(pop_revs), len(data)

	pop_tokens = get_tokens(str(pop_text))
	
	finder = BigramCollocationFinder.from_words(pop_tokens)
	finder.apply_freq_filter(4)
	if finder:
		bestbigrams = best_bigram_collector(finder, 5, title)

	finder = TrigramCollocationFinder.from_words(pop_tokens)

	if finder:
		besttrigrams = best_trigram_collector(finder, 5, title)
	
	#print bestbigrams, besttrigrams
	
	keywords = [item for sublist in bestbigrams for item in sublist] + [item for sublist in besttrigrams for item in sublist]

	print len(pop_revs)
	count = [0]*len(pop_revs)
	i = 0
	for rev in pop_revs:
		if len(rev)>0:
			for word in get_tokens(str(rev)):
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
				hold = hold + " <strong>"+word + "</strong> "
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
	poplabel = "Reviews from <strong>" + date1.strftime("%B") + " " + str(date1.year) + "</strong> to <strong>" + date2.strftime("%B") + " " + str(date2.year) + "</strong>. " 

	return boldrevs, poplabel
	
