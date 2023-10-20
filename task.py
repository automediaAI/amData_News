
##############
#### Data Puller for News ####
#################
## Calls NewsAPI to pull a news. Goes to Airtable table to get what news to pull. Then calls NewsAPI each time to get the data. Saves individually in same airtable. Also puts combined in another service dump table. 
##############
## Ticket: https://www.notion.so/automedia/Create-NewsAPI-Headlines-service-91c8a353fe8d4ce1b9f39844b01605c0 
#############


### CHECKS 
## Is it optimal to save in JSON then pull back, vs just keeping it all in memory in TinyDB? 


## Declarations 
import os
import json
import uuid
import boto3 #to upload larger files to S3
from botocore.exceptions import ClientError
from airtable import Airtable
from datetime import date, datetime, timedelta
from amNews_NewsAPI import newscaller
from amNews_BingAPI import bingnewscaller
from amNews_RedditAPI import redditCallerNews, redditCallerImage
# from amLibrary_Filters import newsClean, newsSummarized, newsCheckResult
from amLibrary_Filters import newsClean, newsCheckResult
from tinydb import TinyDB, Query # To create local DB 
from amService_Nlp import ner_caller
from amService_ChatGPT import summarize_with_gpt 

## Airtable settings 
base_key = os.environ.get("PRIVATE_BASE_KEY")
table_name_news = os.environ.get("PRIVATE_TABLE_NAME_NEWSPAYLOAD") #What to pull
table_name_dump = os.environ.get("PRIVATE_TABLE_NAME_SERVICEDUMP") #Output dump
api_key_airtable = os.environ.get("PRIVATE_API_KEY_AIRTABLE")
airtable_news = Airtable(base_key, table_name_news, api_key_airtable)
airtable_dump = Airtable(base_key, table_name_dump, api_key_airtable)

## Create a TinyDB instance and specify the database file
db = TinyDB('NewsPull.json')

## Amazon S3 settings  
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
aws_region='us-west-1' #Manual while creating the bucket 

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

UUID = 'NewsData-'+str(uuid.uuid1()) #to be used later


#Uploads single json, or list to data_output of record ID as given
def uploadData(inputDictList, recToUpdate):
	recID = recToUpdate
	if isinstance(inputDictList, dict):
		fields = {'output': json.dumps(inputDictList)}
		# fields = {'data_output': str(inputDictList)} #Seems if I do str thats same too
	else:
		fields = {'output': str(inputDictList)}
	airtable_news.update(recID, fields)

# Dumping to service Dump after all is run
def dumpToAirtable(inputURL):
	time_pulled = str(datetime.now())
	amService = 'amData_News'
	data_output = str(inputURL)
	fields = {'UUID':UUID, 'time_pulled':time_pulled, 'data_output': data_output, 'amService':amService }
	airtable_dump.insert(fields)

# # Dumping to service Dump after all is run
def dumpToS3(file_name, bucket='amnewsbucket', object_name=None):
    # If S3 object_name was not specified, use file_name
    url_s3 = f"https://{bucket}.s3-us-west-2.amazonaws.com/{file_name}" #Manually creating structure
    object_name = file_name
    try:
        response = s3.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL':'public-read'})
        return url_s3
    except ClientError as e:
        return ('🚫Error uploading to S3: '+str(e))

def dumpData(table_output, filename_pre):
	filename = (filename_pre + UUID+'.txt')
	#Creating a local text file 
	f = open(filename,"w")
	f.write( str(table_output) )
	f.close()
	url_s3_file = dumpToS3(filename) #uploading to S3 and getting file back
	dumpToAirtable(url_s3_file) #Adding final output to service dump
	os.remove(filename) #deleting file after upload
	print('Dump Upload complete.')


# Running through rows of news, calling newsAPI, uploading data back
def updateNewsLoop():
	print('Started updateNewsLoop loop..') #Extra to keep app going 
	table_output = [] #Final data of entire pull
	table_output_unclean = [] #Data pulled directly without cleaning
	allRecords = airtable_news.get_all() #Get all records 
	print('All records recieved in updateNewsLoop..') #Extra to keep app going 
	for i in allRecords:
		if "Prod_Ready" in i["fields"]: #Only working on prod ready ie checkboxed
			print('Started row..') #Extra to keep app going 
			if "Service" in i["fields"]:
				# Basic payload, common to all
				payload_native = i["fields"]["payload"]
				payload_json = json.loads(payload_native)
				rec_ofAsked = i["id"] #Airtable record with query
				query_name = i["fields"]["Name"] #Just to differentiate what is being called
				# print(payload_json)
				# print(query_name)
				# Calling News service per ask
				if i["fields"]["Service"].lower()  == 'newsapi': #Only pulling if NewsAPI 	
					row_output = newscaller(payload_json, query_name) #NewsAPI output for this call
					# row_output = newsClean(row_output_unclean)
				elif i["fields"]["Service"].lower()  == 'bing': #Only pulling if NewsAPI 	
					row_output = bingnewscaller(payload_json, query_name) #NewsAPI output for this call
					# row_output = row_output_unclean
					# row_output = newsClean(row_output_unclean)
				elif i["fields"]["Service"].lower()  == 'reddit': #Only pulling if Reddit	
					row_output = redditCallerNews(payload_json, query_name) #NewsAPI output for this call
					# row_output = newsClean(row_output_unclean)
				elif i["fields"]["Service"].lower()  == 'redditimage': #Only pulling if Reddit	
					row_output = redditCallerImage(payload_json, query_name) #NewsAPI output for this call
					# row_output = row_output_unclean
				else:
					row_output = "🚫 Query requested is invalid"
				# Appending rest
				print('Row data pull done in updateNewsLoop..') #Extra to keep app going 	
				try:
					table_output.append(row_output) #Adding to all data
					table_output_unclean.append(row_output_unclean) #Adding to all data
				except Exception:
					print ("🚫 Error saving article")
					pass
				## Running Text Cleaning and Image Cleaning functions 
				data_toUpload = row_output #Uploading clean data
				
				## Update to tinyDB
				for data_TinyDBNews in data_toUpload:
					db.insert(data_TinyDBNews)
				print('Row output pushed to TinyDB')
				
				# data_toUpload = row_output #Uploading clean data
				uploadData(data_toUpload, rec_ofAsked) #Upload back to Airtable 
				print('Row output pushed to Airtable')


	# dumpData(table_output, "NewsCleanUnsummarized") #Upload dump to S3 as text


## Basic function that just pulls the TinyDB created JSON and 


## Loop doing all NER work in one go 
def updateNER(key_for_NER):
	# Load data from TinyDB
	data = db.all()
	for item in data:
		news_article_content_mercury = item.get(key_for_NER, '')
		try:
			keywords_ner = ner_caller(news_article_content_mercury)
		except Exception as ex:
			print("NER Caller failed")
			keywords_ner = None
		# Update the keywords_article field
		item['keywords_article'] = keywords_ner
	# Write the modified data back to TinyDB
	db.truncate()  # Clear the existing data
	for item in data:
		db.insert(item)  # Insert the updated records back
	return None 

	# ## Doing it the JSON file way 
	# # Read the JSON file
	# with open(input_file, 'r') as f:
	# 	data = json.load(f)	
	# # Modify the data
	# with open(input_file, 'w') as f:
	# 	json.dump(data, f, indent=4)


## Loop doing all the News Clean Filters 
def updateFilterCheck():
	# Load data from TinyDB
	data = db.all()
	for item in data:
		filter_check = newsCheckResult(item)
		# Update the keywords_article field
		item['filterCheck_Pass'] = filter_check 
	# Write the modified data back to TinyDB
	db.truncate()  # Clear the existing data
	for item in data:
		db.insert(item)  # Insert the updated records back
	return None 

## Using new ChatGPT based summarization 
def updateNewsSummary():
	# Load data from TinyDB
	data = db.all()
	for item in data:
		news_article_content = item.get(content_article, '') if item.get('filterCheck_Pass', {}).get('READY', False) else ''
		try:
			summarized_text = summarize_with_gpt(news_article_content)
		except Exception as ex:
			print("ChatGPT summarization failed")
			summarized_text = None
		# Update the keywords_article field
		item["summarized_article"] = summarized_text 
	# Write the modified data back to TinyDB
	db.truncate()  # Clear the existing data
	for item in data:
		db.insert(item)  # Insert the updated records back
	return None 


# ## Using existing Spacy based summarizer 
# def updateNewsSummary():
# 	print('Started loop in updateNewsSummary..') #Extra to keep app going 
# 	table_output = [] #Final data of entire pull
# 	allRecords = airtable_news.get_all() #Get all records 
# 	print('All records recieved in updateNewsSummary..') #Extra to keep app going 
# 	for i in allRecords:
# 		if "Prod_Ready" in i["fields"]: #Only working on prod ready ie checkboxed
# 			print('Started row in updateNewsSummary..') #Extra to keep app going 
# 			payload_native = i["fields"]["output"] #Getting column on unsummarized data
# 			if isinstance(payload_native, list) or isinstance(payload_native, dict):
# 				payload_json = payload_native
# 			else:
# 				payload_json = eval(payload_native)
# 			rec_ofAsked = i["id"] #Airtable record with query
# 			row_output = newsSummarized(payload_json) #Summarized data
# 			print('Row data complete in updateNewsSummary..')

# 			uploadData(row_output, rec_ofAsked) #Upload back to Airtable 
# 			table_output.append(row_output) #Adding to all data
# 			print('Row complete in updateNewsSummary..')
# 	dumpData(table_output, "NewsSummarized")

## ACTUAL EXECUTION of Tasks in sequence 
print ('======== [ Entering news pull loop]  ========')
updateNewsLoop()

print ('======== [ Entering data quality check]  ========')
print ('======== FILTERS CHECK ========')
updateFilterCheck()

print ('======== [ Entering data enrichment]  ========')
print ('======== Adding NER data ========')
updateNER('description_article')
print ('======== Adding Summarized data ========')
updateNewsSummary()
print ('======== [ Exiting news pull loop]  ========')