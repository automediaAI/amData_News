########################################
############## MERCURIAL ###############
###### Pulls data from Mercury API #####
########################################
 

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
		abort(400) #This abort is not correct since its not a defined function, actually is of flask. Instead use raise error 
	
	if response: #Using logic here that requests does validation for you https://realpython.com/python-requests/
		page_data = response.json() #Data to save | Standards requests way of saving 
		# print(page_data)
		# print(page_data.get("error"))

		if page_data.get("error"):
			print('🚫 Mercury failed for URL:', str(article_in))
			mercurized_article_data = "error"
			return mercurized_article_data

		###### Compiling output ######
		mercurized_article_data = {
			"mercuryAPI_response"	: str(response.status_code), #todo do something with it
			"url_article"			: str(page_data.get("url","")),
			"title_article"			: str(page_data.get("title","")),
			"description_article" 	: "",
			"urtToImage_article"	: str(page_data.get("lead_image_url","")),
			"publishedAt_article" 	: str(page_data.get("date_published","")),
			"content_article" 		: str(page_data.get("content","")).strip(),
			"article_author"		: str(page_data.get("author",""))
			}

		###### Output ######
		return mercurized_article_data #returns a dict

	else:
		print('🚫 Mercury failed for URL:', str(article_in))
		mercurized_article_data = "error"
		return mercurized_article_data


# ##### Test ######
# article_to_get = "https://www.msn.com/en-us/news/world/juan-orlando-hernández-ex-honduras-president-agrees-to-extradition-to-the-us/ar-AATTjm4"
# article_to_get = "https://www.cnn.com/2020/02/15/us/sex-and-the-city-actress-lynn-cohen-dies-trnd/index.html"
# article_to_get = "https://www.aa.com.tr/en/middle-east/israel-worried-by-us-plans-to-lift-icc-sanctions/2124920"
# article_to_get = "https://www.msn.com/en-us/money/realestate/another-housing-bubble-we-re-skating-close-to-one-says-realtorcom-economist/ar-AAWxwnD" #This makes is crap out
# article_to_get = "https://www.carscoops.com/2022/05/what-do-you-prefer-in-dashboards-digital-analog-or-a-mix-of-the-two/" #This makes is crap out
# article_to_get = "https://www.newsobserver.com/money/new-car-prices-selling-below-msrp/" #This makes is crap out
# print(mercury_caller(article_to_get))
