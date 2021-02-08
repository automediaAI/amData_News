
##############
#### Library of Functions that add new data ####
#################
## Calls a few generic sources to get new data from anything existing ie for value add
##############
## Filling this py file from older amStorehouse, and then will break into separate common file so other services can call this too
#############

import requests
from urllib.parse import urlparse #to get URL info if no OG
from bs4 import BeautifulSoup

######### Get Site Name from Opengraph Data ##########
def url_to_sitename(url_in): #Only works for a single use case of opengraph
	try: #adding overall in case any error
		response = requests.get(url_in, timeout=15)
		soup = BeautifulSoup(response.text, 'html.parser')
		try:
			sitename = soup.find("meta", property ="og:site_name").attrs["content"]
		except: #from https://stackoverflow.com/a/41919945/9231911
			print("ran into exception with bs4")
			parsed_uri = urlparse(url_in)
			domain = '{uri.netloc}'.format(uri=parsed_uri)
			result = domain.replace('www.', '')  # as per your case
			sitename = result.title()
			# sitename = urlparse.urlparse(url_in).hostname
		# sitename = soup.find("meta", name="twitter:site").attrs["content"] #need to create these too
		return sitename
	except:
		print ("🚫URL to Sitename crapped")
		return ""
## Testing
# print(url_to_sitename('https://www.bbc.com/news/business-55722542'))
# print(url_to_sitename('https://www.youtube.com/watch?v=XV9SBK1vzu4'))
# print(url_to_sitename('https://www.theatlantic.com/health/archive/2021/01/coronavirus-vaccine-masks-how-much-longer/617747/'))
# print(url_to_sitename('https://www.globaltimes.cn/page/202101/1213707.shtml')) #No sitename in PG
# print(url_to_sitename('https://www.w3schools.com/python/python_try_except.asp')) #No sitename in PG
# print(url_to_sitename('https://www.aa.com.tr/en/middle-east/israel-worried-by-us-plans-to-lift-icc-sanctions/2124920')) #No sitename in PG
# print(url_to_sitename('https://www.seattletimes.com/nation-world/mutated-virus-may-reinfect-people-already-stricken-once-with-covid-19-sparking-debate-and-concerns/')) #Requests.get not working