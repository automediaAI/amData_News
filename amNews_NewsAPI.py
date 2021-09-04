
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
from amService_Summarizer import summarization_caller #Summarization service to create summary

# NewsAPI Settings
api_key_newsAPI = os.environ.get("PRIVATE_API_KEY_NEWSAPI")
newsapi = NewsApiClient(api_key=api_key_newsAPI)

# Function for calling NewsAPI 
def newscaller(input_config, queryName):
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
	# articlecount = 0
	for news_article in articles_source:
		article_content = news_article["content"] #Getting content earlier to summarize
		summarized_content = summarization_caller(article_content) #Pulling summary data based on content
		output_article_single = {
				# 'recID'					: str(articlecount), 
				'source_API'			: 'newsAPI', 
				'query_name'			: queryName,   #Name of record in amPayload table
				'source_article'		: str(news_article["source"]["name"]).strip(),
				'title_article' 		: str(news_article["title"]).strip(),
				'description_article' 	: str(news_article["description"]).strip(),
				'url_article' 			: str(news_article["url"]).strip(),
				'urtToImage_article' 	: news_article["urlToImage"],
				'publishedAt_article' 	: news_article["publishedAt"],
				'content_article' 		: article_content,
				'summarized_article'    : summarized_content,
				}
		output_article_all.append(output_article_single)
		# articlecount += 1

	# Final output from newsAPI run
	return output_article_all
