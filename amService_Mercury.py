########################################
############## MERCURIAL ###############
###### Pulls data from Mercury API #####
########################################
 
"""

ToDo
. BSoup needed? / HTML text string symbol 

"""

###### Declarations ######

import os
import json
import requests
from datetime import datetime
# from bs4 import BeautifulSoup
now = datetime.now()
import os, sys
from os.path import dirname, abspath
# print (dir_source) #To check the path of the DIR

###### Manually hosted Mercury Server on AWS Lambda ######
mercury_post = os.environ.get("MERCURY_POST_ENDPOINT")
mercury_get = os.environ.get("MERCURY_GET_ENDPOINT")
endpoint_of_mercury_post = mercury_post
endpoint_of_mercury_get = mercury_get

###### Caller Mercury and get data ######
def mercury_caller(article_in):

	###### CALL API, PASS PAYLOAD, GET DATA, ENCODE TO JSON ######
	method_in = "POST" 
	if method_in == "POST":
		url_in = endpoint_of_mercury_post 
		response = requests.post(url_in, json={'url': article_in, 'contentType': 'text'}) #tins API only takes text
	elif method_in == "GET":
		url_in = endpoint_of_mercury_get+"?contentType=text&url="+article_in #Dont use this way, but works if needed since API supports it 
		response = requests.get(url_in) 
	else:
		abort(400)
	
	if response: #Using logic here that requests does validation for you https://realpython.com/python-requests/
		page_data = response.json() #Data to save | Standards requests way of saving 

		###### Compiling output ######
		mercurized_article_data = {
			"mercuryAPI_response"	: str(response.status_code), #todo do something with it
			"url_article"			: str(page_data.get("url","")),
			"title_article"			: str(page_data.get("title","")),
			"description_article" 	: "",
			"urtToImage_article"	: str(page_data.get("lead_image_url","")),
			"publishedAt_article" 	: str(page_data.get("date_published","")),
			"content_article" 		: str(page_data.get("content","")),
			"article_author"		: str(page_data.get("author",""))
			}

		###### Output ######
		return mercurized_article_data #returns a dict

	else:
		print('🚫Mercury API has crapped out, didnt return anything')
		mercurized_article_data = "error"
		return mercurized_article_data


# ##### Test ######
# article_to_get = "https://www.cnn.com/2020/02/15/us/sex-and-the-city-actress-lynn-cohen-dies-trnd/index.html"
# mercury_caller(article_to_get)
