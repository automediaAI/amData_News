
##############
#### Data Puller for News ####
#################
## Calls NewsAPI to pull a news. Goes to Airtable table to get what news to pull. Then calls NewsAPI each time to get the data. Saves individually in same airtable. Also puts combined in another service dump table. 
##############
## Ticket: https://www.notion.so/automedia/Create-NewsAPI-Headlines-service-91c8a353fe8d4ce1b9f39844b01605c0 
#############


## Declarations 
import os
import json
import uuid
from airtable import Airtable
from newsapi import NewsApiClient # pip install newsapi-python (not newsapi - thats an unused one)
from datetime import date, datetime, timedelta

# NewsAPI Settings
# api_key_newsAPI = os.environ.get("PRIVATE_API_KEY_NEWSAPI")
# newsapi = NewsApiClient(api_key=api_key_newsAPI)
newsapi = NewsApiClient(api_key='cf82bb056f264d228fa0a959481a332c') #Delete in prod

# Airtable settings 
# base_key = os.environ.get("PRIVATE_BASE_KEY")
# table_name_news = os.environ.get("PRIVATE_TABLE_NAME_NEWSPAYLOAD") #What to pull
# table_name_dump = os.environ.get("PRIVATE_TABLE_NAME_SERVICEDUMP") #Output dump
# api_key_Airtable = os.environ.get("PRIVATE_API_KEY_AIRTABLE")
# airtable_news = Airtable(base_key, table_name_news, api_key)
# airtable_dump = Airtable(base_key, table_name_dump, api_key)
airtable_news = Airtable("app1GvM6I6bnrucdP", "amPayload_News", "keyuziq0Tc5OPKbIP")
airtable_dump = Airtable("app1GvM6I6bnrucdP", "serviceDataDump", "keyuziq0Tc5OPKbIP")

# Function for calling NewsAPI 
def newscaller(input_config):
	newscaller_config = input_config #just from older code
	endpoint = newscaller_config['endpoint'].lower()
	query_config = newscaller_config['query']

	# Calling NewsAPI based on endpoint
	if endpoint == 'headlines':
		source = newsapi.get_top_headlines(**query_config) #New find by tin 
	elif endpoint == 'everything':
		source = newsapi.get_everything(**query_config)
	else:
		print("🚫Endpoint requested is invalid") 
		source = {}

	########################     RAW DATA    ############################
	#Recording the data from the original Dictionary

	status_source = source["status"]
	results_count = source["totalResults"]
	articles_source = source["articles"] #MAIN CONTENT SOURCE Variable

	## Organizing data
	output_article_all = []
	articlecount = 0

	for news_article in articles_source:
		articlecount += 1
		output_article_single = {
				'recID_article'			: str(articlecount), 
				'source_article'		: str(news_article["source"]["name"]).strip(),
				'title_article' 		: str(news_article["title"]).strip(),
				'description_article' 	: str(news_article["description"]).strip(),
				'url_article' 			: str(news_article["url"]).strip(),
				'urtToImage_article' 	: news_article["urlToImage"],
				'publishedAt_article' 	: news_article["publishedAt"],
				'content_article' 		: news_article["content"],
				}
		output_article_all.append(output_article_single)

	# Final output from newsAPI run
	return output_article_all


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
def dumpData(inputDictList):
	UUID = 'NewsData-'+str(uuid.uuid1())
	time_pulled = str(datetime.now())
	amService = 'amData_News'
	fields = {'UUID':UUID, 'time_pulled':time_pulled, 'data_output': str(inputDictList), 'amService':amService }
	airtable_dump.insert(fields)

# Running through rows of news, calling newsAPI, uploading data back
def updateNewsLoop():
	table_output = [] #Final data of entire pull
	allRecords = airtable_news.get_all() #Get all records 
	for i in allRecords:
		if "Prod_Ready" in i["fields"]: #Only working on prod ready ie checkboxed
			payload_native = i["fields"]["payload"]
			payload_json = json.loads(payload_native)
			rec_ofAsked = i["id"]
			
			row_output = newscaller(payload_json) #NewsAPI output for this call
			
			table_output.append(row_output) #Adding to all data
			data_toUpload = row_output #In case some operation needed
			uploadData(data_toUpload, rec_ofAsked) #Upload back to Airtable 
			print('Row complete..')
	
	dumpData(table_output) #Adding final output to service dump
	print('Table complete.')


updateNewsLoop()