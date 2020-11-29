

from newsapi import NewsApiClient

# Init
newsapi = NewsApiClient(api_key='cf82bb056f264d228fa0a959481a332c')

# /v2/top-headlines
top_headlines = newsapi.get_top_headlines(country='us',)

print ('Top headlines', top_headlines)
print ('Top headlines, TYPE', type(top_headlines))