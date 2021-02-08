import unittest

from amLibrary_DataAddFunctions import url_to_sitename
from amNews_RedditAPI import redditCallerNews, redditCallerImage

class Test(unittest.TestCase):
    """
    The basic class that inherits unittest.TestCase
    """

    def test_sitename_0(self):
        print("Start sitename test 0\n")
        sitename = url_to_sitename('https://www.bbc.com/news/business-55722542')
        self.assertTrue(sitename, "BBC News")

    def test_sitename_1(self):
        print("Start sitename test 1\n")
        sitename = url_to_sitename('https://www.seattletimes.com/nation-world/mutated-virus-may-reinfect-people-already-stricken-once-with-covid-19-sparking-debate-and-concerns/')
        self.assertTrue(sitename, "Seattletimes.Com")

    # def test_(self):
    # 	payload_json = {'endpoint': 'not logged in', 'query': {'subreddit_name': 'China_Flu', 'sort_order': 'top', 'items_limit': 6}}
    # 	query_name = "Virus Updates (REDDIT)"
    # 	row_output_unclean = redditCallerNews(payload_json, query_name)
    # 	print(row_output_unclean)
    # 	self.assertTrue(True)