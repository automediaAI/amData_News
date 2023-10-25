
##############
#### Data Puller for News ####
#################
## Calls NewsAPI to pull a news. Calls NewsAPI each time to get the data. Is called by another function that passes payload. 
##############
## Ticket: https://www.notion.so/automedia/Create-NewsAPI-Headlines-service-91c8a353fe8d4ce1b9f39844b01605c0 
#############

## Declarations 
import os
from newsapi import NewsApiClient # pip install newsapi-python (not newsapi - thats an unused one)
# from amService_Summarizer import summarization_caller #Summarization service to create summary
from amService_Mercury import mercury_caller #Mercury service to get all article data 
# from amService_Nlp import ner_caller

# NewsAPI Settings
api_key_newsAPI = os.environ.get("PRIVATE_API_KEY_NEWSAPI")
newsapi = NewsApiClient(api_key=api_key_newsAPI)

# Function for calling NewsAPI 
def newscaller(input_config, queryName):
	print ("[[ Data being pulled from NEWS API ]]")
	newscaller_config = input_config #just from older code
	endpoint = newscaller_config['endpoint'].lower()
	query_config = newscaller_config['query']

	# Calling NewsAPI based on endpoint
	if endpoint == 'headlines':
		source = newsapi.get_top_headlines(**query_config) #New find by tin 
	elif endpoint == 'everything':
		source = newsapi.get_everything(**query_config)
	else:
		print("🚫 Endpoint requested is invalid") 
		source = {}

	########################     RAW DATA    ############################
	#Recording the data from the original Dictionary

	status_source = source["status"]
	results_count = source["totalResults"]
	articles_source = source["articles"] #MAIN CONTENT SOURCE Variable

	## Organizing data
	output_article_all = []
	for news_article in articles_source:
		# debug
		# print(news_article)
		# run mercury processing
		url_to_check = str(news_article["url"]).strip()
		# print('URL to mercury: ', url_to_check)
		mercury_data = mercury_caller(url_to_check) #Getting Data from Mercury
		news_article_content = ""
		if mercury_data == 'error':
			print('🚫 Article skipped since Mercury crapped out')
			mercury_worked_status = False
			news_article_content_mercury = news_article["urlToImage"] #Backup to NewsAPI
			urtToImage_article_mercury = news_article["urlToImage"] #Backup to NewsAPI
		else:
			mercury_worked_status = True
			news_article_content_mercury = mercury_data['content_article'] #To get only content of article from mercury dict
			urtToImage_article_mercury = mercury_data['urtToImage_article'] #To get higher s
			# print(news_article_content)
			#Calling Summarizer
			# summarized_content = summarization_caller(news_article_content_mercury)
			# print(summarizer_content)

		# try: news_article_content_mercury
		# except NameError: keywords_ner = None
		# else:
		# 	try:
		# 		keywords_ner = ner_caller(news_article_content_mercury)
		# 	except Exception as ex:
		# 		print("NER Caller failed")
		# 		keywords_ner = None

		#taking most from BingAPI, adding from Mercury API
		# output_article_single = {
		# 		'source_API'               : 'NewsAPI', 
		# 		'mercury_worked'		   : mercury_worked_status,
		# 		'query_name'               : queryName,   #Name of record in amPayload table   
		# 		'source_article'		   : str(news_article["source"]["name"]).strip(),
		# 		'title_article'            : str(news_article["title"]).strip(),
		# 		'description_article'      : str(news_article["description"]).strip(), #done
		# 		'url_article'              : str(news_article["url"]).strip(), #done
		# 		'urtToImage_article'       : urtToImage_article_mercury, #Using mercury data instead
		# 		'publishedAt_article'      : news_article["publishedAt"],
		# 		'content_article'          : news_article_content_mercury,
		# 		'keywords_article'         : keywords_ner,
		# 		# 'summarized_article'       : summarized_content,
		# 		}
		# output_article_all.append(output_article_single)

		output_article_single = {
				'source_API'               : 'NewsAPI', 
				'mercury_worked'		   : mercury_worked_status,
				'query_name'               : queryName,   #Name of record in amPayload table   
				'source_article'		   : str(news_article.get("source", {}).get("name", "")).strip(), # Modified to handle KeyError
				'title_article'            : str(news_article.get("title", "")).strip(), # Modified to handle KeyError
				'description_article'      : str(news_article.get("description", "")).strip(), # Modified to handle KeyError
				'url_article'              : str(news_article.get("url", "")).strip(), # Modified to handle KeyError
				'urtToImage_article'       : urtToImage_article_mercury, #Using mercury data instead
				'publishedAt_article'      : news_article.get("publishedAt", ""), # Modified to handle KeyError
				'content_article'          : news_article_content_mercury,
				# 'keywords_article'         : keywords_ner,
				# 'summarized_article'       : summarized_content,
		}
		output_article_all.append(output_article_single)


	# Final output from newsAPI run
	return output_article_all

	
	
	###### CODE for just using data pulled from NewsAPI ie not using mercuty
	## Organizing data 
	# output_article_all = []
	# # articlecount = 0
	# for news_article in articles_source:
	# 	article_content = news_article["content"] #Getting content earlier to summarize
	# 	# summarized_content = summarization_caller(article_content) #Pulling summary data based on content
	# 	output_article_single = {
	# 			# 'recID'					: str(articlecount), 
	# 			'source_API'			: 'newsAPI', 
	# 			'query_name'			: queryName,   #Name of record in amPayload table
	# 			'source_article'		: str(news_article["source"]["name"]).strip(),
	# 			'title_article' 		: str(news_article["title"]).strip(),
	# 			'description_article' 	: str(news_article["description"]).strip(),
	# 			'url_article' 			: str(news_article["url"]).strip(),
	# 			'urtToImage_article' 	: news_article["urlToImage"],
	# 			'publishedAt_article' 	: news_article["publishedAt"],
	# 			'content_article' 		: article_content,
	# 			# 'summarized_article'    : summarized_content,
	# 			}
	# 	output_article_all.append(output_article_single)
	# 	# articlecount += 1

	# # Final output from newsAPI run
	# return output_article_all
