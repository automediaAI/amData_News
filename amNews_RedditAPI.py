#Service that loops through Airtable payload, find what news to pull and gets it from Reddit

##############
#### Data puller for news or posts from Reddit ####
#################
## Reddit Scraper for news, but making it general purpose as much as possible
##############
## Ticket: https://www.notion.so/automedia/Create-NewsAPI-Reddit-Headlines-service-91c8a353fe8d4ce1b9f39844b01605c0 
#############

import os
import praw
from amService_Mercury import mercury_caller 

# Reddit credentials
reddit_client_id = os.environ.get("PRIVATE_REDDIT_CLIENTID")
reddit_client_secret = os.environ.get("PRIVATE_REDDIT_SECRET")
reddit = praw.Reddit(
     client_id=reddit_client_id,
     client_secret=reddit_client_secret,
     user_agent="am_agent_reddit_v1"
)

# Function to give back submissions in ordered list
def all_submissions(posts_object, queryName):
	submissions_list = []
	recIDcount = 0
	for submission in posts_object:
		recIDcount += 1
		submission_dict = {
			'recID':recIDcount,
			'query_name': queryName, #Name of record in amPayload table
			'source_API': 'redditAPI', 
			'reddit_title':submission.title,
			'reddit_body':submission.selftext,
			'reddit_score':submission.score,
			'reddit_id':submission.id,
			'reddit_comments_total':submission.num_comments,
			'reddit_created':submission.created,
			'article_url':submission.url, 
			'reddit_path':'https://www.reddit.com'+str(submission.permalink) #URL to post
		}
		submissions_list.append(submission_dict)
	return submissions_list 

# Function that returns posts object
def all_posts(subreddit_name, sort_order, items_limit, queryName):
	subreddit = reddit.subreddit(subreddit_name)
	sort_order = sort_order.lower()
	if sort_order == "top":
		post_ordered = subreddit.top(limit=items_limit)
	elif sort_order == "new":
		post_ordered = subreddit.new(limit=items_limit)
	elif sort_order == "hot":
		post_ordered = subreddit.hot(limit=items_limit)
	elif sort_order == "rising":
		post_ordered = subreddit.rising(limit=items_limit)
	else:
		post_ordered = subreddit.hot(limit=items_limit)
	all_posts = all_submissions(post_ordered, queryName)
	return all_posts

# Task function to call and get posts from Reddit
def get_posts(reddit_query, queryName):
	payload = reddit_query['query']
	posts_returned = all_posts(payload['subreddit_name'], payload['sort_order'], payload['items_limit'], queryName)
	return posts_returned

# Task function to call Mercury and 
def reddit_caller(reddit_query, queryName):
	reddit_LinkList = get_posts(reddit_query, queryName)
	for article in reddit_LinkList:
		url_to_check = article['article_url']
		print('URL to mercury: ', url_to_check)
		mercury_data = mercury_caller(url_to_check)
		if mercury_data == 'error':
			print ('🚫Article skipped since Mercury crapped out')
		else:
			article.update(mercury_data) #format is already goood
	return reddit_LinkList

# # Testing
# reddit_query = {'query':{
# 	# Testing 
# 	'subreddit_name':"worldnews", #should come from API 
# 	'sort_order':"new",
# 	'items_limit':1
# }}
# queryName = "World News"

# print(reddit_caller(reddit_query, queryName))
