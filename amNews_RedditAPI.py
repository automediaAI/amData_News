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
from amLibrary_DataAddFunctions import url_to_sitename

## Reddit credentials 
reddit_client_id = os.environ.get("PRIVATE_REDDIT_CLIENTID")
reddit_client_secret = os.environ.get("PRIVATE_REDDIT_SECRET") #using public for now 
reddit = praw.Reddit(
     client_id=reddit_client_id,
     client_secret=reddit_client_secret,
     user_agent="am_agent_reddit_v1"
)

# Function to give back submissions in ordered list
def all_submissions(posts_object, queryName):
	submissions_list = []
	# recIDcount = 0
	for submission in posts_object:
		submission_dict = {
			# 'recID':recIDcount,
			'query_name': queryName, #Name of record in amPayload table
			'source_API': 'redditAPI', 
			'reddit_title':submission.title,
			'reddit_body':submission.selftext,
			'reddit_score':submission.score,
			'reddit_id':submission.id,
			'reddit_comments_total':submission.num_comments,
			'reddit_created':submission.created,
			'submission_url':submission.url, 
			'reddit_path':'https://www.reddit.com'+str(submission.permalink) #URL to post
		}
		submissions_list.append(submission_dict)
		# recIDcount += 1
	return submissions_list 

# Function that returns posts object
def all_posts(subreddit_name, sort_order, items_limit, queryName):
	get_extra = 20 #this will always get more posts than asked for in case data not good, then next functions return correct qty
	subreddit = reddit.subreddit(subreddit_name)
	sort_order = sort_order.lower()
	if sort_order == "top":
		post_ordered = subreddit.top(time_filter="day", limit=items_limit+get_extra) #hard coding for Top to get todays data, else defaults to all
	elif sort_order == "new":
		post_ordered = subreddit.new(limit=items_limit+get_extra)
	elif sort_order == "hot":
		post_ordered = subreddit.hot(limit=items_limit+get_extra)
	elif sort_order == "rising":
		post_ordered = subreddit.rising(limit=items_limit+get_extra)
	else:
		post_ordered = subreddit.hot(limit=items_limit+get_extra)
	all_posts = all_submissions(post_ordered, queryName)
	return all_posts

# Task function to call and get posts from Reddit
def get_posts(reddit_query, queryName):
	payload = reddit_query['query']
	posts_returned = all_posts(payload['subreddit_name'], payload['sort_order'], payload['items_limit'], queryName)
	return posts_returned

# Task function to call Mercury and 
def redditCallerNews(reddit_query, queryName):
	# Getting redding submissions
	reddit_LinkList = get_posts(reddit_query, queryName)
	# Quick check if item limit is given, since not using in NewsAPI - may evolve to remove later
	if reddit_query['query']['items_limit']:
		count_asked = reddit_query['query']['items_limit']
	else:
		count_asked = 6 
	#Getting Mercury data for reddit articles
	for article in reddit_LinkList:
		url_to_check = article['submission_url']
		print('URL to mercury: ', url_to_check)
		mercury_data = mercury_caller(url_to_check) #Getting Data from Mercury
		if mercury_data == 'error':
			print ('🚫Article skipped since Mercury crapped out')
		else:
			article.update(mercury_data) #format is already goood
		source_news = url_to_sitename(url_to_check) #Getting Sitename from OpenGraph
		if source_news: #If value is returned from Open Graph
			article['source_article'] = source_news
		else: #If nothing is returned from OpenGraph
			article['source_article'] = ""
	if len(reddit_LinkList) <= count_asked: #if less items than asked 
		return reddit_LinkList
	else:
		return reddit_LinkList[:count_asked] #if more items than asked 

def redditCallerImage(reddit_query, queryName):
	# Quick check if item limit is given, since not using in NewsAPI - may evolve to remove later
	if reddit_query['query']['items_limit']:
		count_asked = reddit_query['query']['items_limit']
	else:
		count_asked = 6 
	# Getting reddit data
	reddit_posts = get_posts(reddit_query, queryName) #org list of all posts 
	reddit_ImageList = [] #will have ones with image 
	for post in reddit_posts:
		url_to_check = post['submission_url']
		if '.jpg' in url_to_check or '.jpeg' in url_to_check or '.jpeg' in url_to_check or '.png' in url_to_check or '.gif' in url_to_check or '.gifv' in url_to_check:
			reddit_ImageList.append(post)
		else:
			pass
	if len(reddit_ImageList) == 0:
		return "🚫Query requested is invalid"
	elif len(reddit_ImageList) <= count_asked: #if less items than asked 
		return reddit_ImageList
	else:
		return reddit_ImageList[:count_asked] #if more items than asked 

# Testing
# reddit_query1 = {'query':{
# 	# Testing 
# 	'subreddit_name':"worldnews", #should come from API 
# 	'sort_order':"new",
# 	'items_limit':5
# }}
# queryName1 = "World News"

# print(redditCallerNews(reddit_query1, queryName1))
