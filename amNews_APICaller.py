
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
from datetime import date, datetime, timedelta
from amNews_NewsAPI import newscaller
from amNews_RedditAPI import reddit_caller

# Airtable settings 
base_key = os.environ.get("PRIVATE_BASE_KEY")
table_name_news = os.environ.get("PRIVATE_TABLE_NAME_NEWSPAYLOAD") #What to pull
table_name_dump = os.environ.get("PRIVATE_TABLE_NAME_SERVICEDUMP") #Output dump
api_key_airtable = os.environ.get("PRIVATE_API_KEY_AIRTABLE")
airtable_news = Airtable(base_key, table_name_news, api_key_airtable)
airtable_dump = Airtable(base_key, table_name_dump, api_key_airtable)

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
	if len(str(inputDictList)) <= 100000: #Since airtable free limit. Need to upload to S3 instead
		data_output = str(inputDictList)
	else:
		data_output = "🚫Output was longer than 100k chars, longer than airtable free allows"
	fields = {'UUID':UUID, 'time_pulled':time_pulled, 'data_output': data_output, 'amService':amService }
	airtable_dump.insert(fields)

# Running through rows of news, calling newsAPI, uploading data back
def updateNewsLoop():
	table_output = [] #Final data of entire pull
	allRecords = airtable_news.get_all() #Get all records 
	for i in allRecords:
		if "Prod_Ready" in i["fields"]: #Only working on prod ready ie checkboxed
			if "Service" in i["fields"]:
				# Basic payload, common to all
				payload_native = i["fields"]["payload"]
				payload_json = json.loads(payload_native)
				rec_ofAsked = i["id"]
				query_name = i["fields"]["Name"] #Just to differentiate what is being called
				# Calling News service per ask
				if i["fields"]["Service"].lower()  == 'newsapi': #Only pulling if NewsAPI 	
					row_output = newscaller(payload_json, query_name) #NewsAPI output for this call
				elif i["fields"]["Service"].lower()  == 'reddit': #Only pulling if Reddit	
					row_output = reddit_caller(payload_json, query_name) #NewsAPI output for this call
				else:
					row_output = "🚫Query requested is invalid"
				# Appending rest
				table_output.append(row_output) #Adding to all data
				data_toUpload = row_output #In case some operation needed
				uploadData(data_toUpload, rec_ofAsked) #Upload back to Airtable 
				print('Row complete..')
	
	dumpData(table_output) #Adding final output to service dump
	print('Table complete.')


updateNewsLoop()