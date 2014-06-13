import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import MySQLdb
import sys

def time_data_clean(time_data):
    rating = [0.0]*len(time_data)
    time = [0]*len(time_data)
    rating = [x[0] for x in time_data]
    time = [x[1] for x in time_data]
    return rating, time


def main():
	db = MySQLdb.connect(host="localhost", user="root", db = "home_kitchen")
	cursor = db.cursor()
	tablename = 'all_hk'
	prod_id = sys.argv[1]

#Get time & score from table

	sql = "Select RTime, RScore From " +tablename + " Where PID = " + '"' + prod_id +'";'
	cursor.execute(sql) 
	time_data = cursor.fetchall()
	time_data = sorted(time_data)
	
	
	rating = zip(*time_data)[1]
	time = zip(*time_data)[0]
	
	#plot the review scores with time, raw data
	fig = plt.figure(figsize=(10, 5), dpi=100)  	
  plt.scatter(*zip(*time_data))
  #plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter(useOffset = False))
  plt.title("Ratings with Time")
  plt.ylabel("Ratings")
  plt.xlabel("Time (Unix Timestamp)")
  plt.show()
  
  avg = [0]*len(time)
  avg[0] = rating[0]
  
  for k in range(1, len(time)):
    avg[k]= np.mean(rating[:k])
    
  #plot the average review with time
	fig = plt.figure(figsize=(10, 5), dpi=100)  
	plt.scatter(time, avg)
	plt.title("Avg Rating Over Time")
	plt.ylabel("Avg Rating")
	plt.xlabel("Time (Unix Timestamp)")
	plt.show()
	
	
if __name__ == '__main__':
  main() 
