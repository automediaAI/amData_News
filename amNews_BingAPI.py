
##############
#### Data Puller for News ####
#################
## Calls BingAPI to pull a news. Is called by another function that passes payload. 
##############
## Ticket: https://www.notion.so/automedia/Bing-news-pull-a49f2347dd2745cba50a83148bdc7d64
#############

## Declarations 
import json
import os
import requests

from amService_Mercury import mercury_caller #Mercury service to value add article data
# from amService_Summarizer import summarization_caller #Summarization service to create summary

#Bing Credentials 
subscriptionKey = os.environ.get("BING_SEARCH_V7_SUBSCRIPTION_KEY")
endpoint_list = {
    'search' : 'https://api.bing.microsoft.com/v7.0/news/search',
    'trending' : 'https://api.bing.microsoft.com/v7.0/news/trendingtopics',
    'category'  :'https://api.bing.microsoft.com/v7.0/news',
}
headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}

# Small text cleaning function to remove 
def pidRemover(url_in):
    try:
        url_out = url_in.replace('&pid=News', '')
        return url_out
    except:
        return url_in

# Function for calling NewsAPI 
def bingnewscaller(input_config, queryName):
    ## Query payload creation
    endpoint_name = input_config['endpoint'] 
    endpoint = endpoint_list[endpoint_name]
    query_params = input_config['query']
    params = query_params   

    ## Calling the API 
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        source = response.json()
    except Exception as ex:
        print("🚫API crapped out") 
        source = {}

    ########################     RAW DATA    ############################
    #Recording the data from the original Dictionary
    articles_source = source["value"] #Article content from BingAPI

    ## Organizing data
    output_article_all = []
    for news_article in articles_source:
        # run mercury processing
        url_to_check = str(news_article["url"]).strip()
        # print('URL to mercury: ', url_to_check)
        mercury_data = mercury_caller(url_to_check) #Getting Data from Mercury
        news_article_content = ""
        if mercury_data == 'error':
            print('🚫Article skipped since Mercury crapped out')
        else:
            news_article_content_mercury = mercury_data['content_article'] #To get only content of article from mercury dict
            urtToImage_article_mercury = mercury_data['urtToImage_article'] #To get higher s
            # print(news_article_content)
            #Calling Summarizer
            # summarized_content = summarization_caller(news_article_content_mercury)
            # print(summarizer_content)

        #taking most from BingAPI, adding from Mercury API
        output_article_single = {
                'source_API'               : 'bing', 
                'query_name'               : queryName,   #Name of record in amPayload table   
                'source_article'           : str(news_article["provider"][0]["name"]).strip(), #done
                'source_icon'              : pidRemover(news_article.get('provider')[0].get('image', {}).get("thumbnail", {}).get("contentUrl","")), #done
                'title_article'            : str(news_article["name"]).strip(), #done
                'description_article'      : str(news_article["description"]).strip(), #done
                'url_article'              : str(news_article["url"]).strip(), #done
                # 'urtToImage_article'       : pidRemover(news_article.get('image', {}).get("thumbnail", {}).get("contentUrl","")), #done
                'urtToImage_article'       : urtToImage_article_mercury, #Using mercury data instead
                'publishedAt_article'      : news_article["datePublished"], #done
                'content_article'          : news_article_content_mercury,
                # 'summarized_article'       : summarized_content,
                }
        output_article_all.append(output_article_single)

    # Final output from newsAPI run
    return output_article_all

### TESTING
# bingnewscaller()