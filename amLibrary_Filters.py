
##############
#### Library of Functions filters Text and Images ####
#################
## For news items makes sure all data is present for image and text using spacy or other tools
##############
## 
#############

## Declarations 
from PIL import Image
import requests
from langdetect import detect #https://pypi.org/project/langdetect/
from profanityfilter import ProfanityFilter ##https://pypi.org/project/profanityfilter/ Manual dict
from amService_Summarizer import summarization_caller #Summarization service to create summary


### TEXT CHECK FUNCTIONS 
## Detects Language of text 
def langDetect(string):
	return detect(string)

## Checks if Language is english 
def langEn(string):
	if langDetect(string) == "en":
		return True

## Checks if word in URL
def checkWord(string, word):
	if string:
		if word in string: 
			return True

## Checks if Youtube in URL ## USE
def checkYoutube(string, word="youtube"):
	return checkWord(string, word)

## Checks if length of word less than something
def lenCheck(string, count=30):
	if len(string) >= count:
		return True

## Returns true if it has profanity for now, or blocked words 
## Using lame one ie more of a word list
def checkBlockWord(string):
	pf = ProfanityFilter()
	return pf.is_clean(string) #True if all good

### IMAGE CHECK FUNCTIONS 
## Checks if image reponse true, used below
def imageExists(url_in):
    if url_in:
        response = requests.get(url_in)
        return True if response else False #checks if url getting response
    else:
        return False

## Gets all details about image 
def getImageDetails(fileURL, location="online"):
    if location == "local":
        im = Image.open(fileURL)
    else:
        im = Image.open(requests.get(fileURL, stream=True).raw)
    imageDetails = {
        "format":im.format,
        "size":im.size,
        "mode": im.mode
    }    
    return imageDetails

## ImageSize Check - Returns True/False if size matches
def checkImageSize(fileURL, checkSize, location="online"):
	try:
		if imageExists(fileURL):
			imageSize = getImageDetails(fileURL, location)["size"]
			if (imageSize[0] >= checkSize[0]) and (imageSize[1] >= checkSize[1]):
				return True
	except:
		return False


### COMBO FUNCTIONS for News Items 

## Checks that news and text is good, else returns false 
# Will keep updating this to add more checks 
def newsCheck(rowDict):
	try: #In case any item in dict doesnt exist then doesnt pass
		if checkBlockWord(rowDict['title_article']) and langEn(rowDict['title_article']) and lenCheck(rowDict['title_article'], count=5) and checkImageSize(rowDict['urtToImage_article'], (10,10)):
			return True
	except KeyError:
		pass

## Function that returns a result of checking different checks
def newsCheckResult(rowDict):
    result_dict = {}  # Dictionary to store individual checks and overall result

    # Check if title_article exists and meets conditions
    result_dict['checkBlockWord_title'] = checkBlockWord(rowDict.get('title_article', ''))
    result_dict['langEn_title'] = langEn(rowDict.get('title_article', ''))
    result_dict['lenCheck_title'] = lenCheck(rowDict.get('title_article', ''), count=5)
    result_dict['checkImageSize_title'] = checkImageSize(rowDict.get('urtToImage_article', ''), (10, 10))

    # Check if all conditions for title_article are True
    result_dict['READY'] = all(result_dict.values())

    # # Append the result_dict to rowDict
    # rowDict['filterCheck_Pass'] = result_dict # If should use or not

    return result_dict




# Returns smaller dict with clean data
def newsClean(allDict):
	cleanList = []
	for i in allDict:
		# print ('Newscheck outcome', newsCheck(i))
		if newsCheck(i):
			cleanList.append(i)
	return cleanList

# Returns summarized version of the news, takes large dict finds content and summarizes 
def newsSummarized(allList):
	for news_article in allList:
		article_content = news_article["content_article"] #Getting content earlier to summarize
		try:
			summarized_content = summarization_caller(article_content) #Pulling summary data based on content
			#logic to see if to use summary or not, will refine more later
			if len(summarized_content) < len(article_content):
				news_article["summarized_article"] = summarized_content
			else:
				news_article["summarized_article"] = article_content
		except Exception as e:
			print('🚫Summarizer API has crapped out, didnt return anything')
			print('news article in question - ')
			print(news_article)
	return allList


## Testing - COMBO 

# newsRow = {
# 	'title_article':"You are a good person",
# 	'urtToImage_article':'https://cdn.24.co.za/files/Cms/General/d/10825/8b335fe7818a46d18a748ca88f492c9f.jpg',
# }

# newsRow = {
# 	'title_article':"You are a good person",
# }

# # print ("Lang check: ", langEn(newsRow['title_article']))
# # print ("Length check: ", lenCheck(newsRow['title_article']))
# # print ("Image size check: ", checkImageSize(newsRow['urtToImage_article'] , (5,5)))
# print ("Final news combo check: ",newsCheck(newsRow))



# newsRows = [{
# 	'title_article':"You are a good person",
# 	'urtToImage_article':'https://cdn.24.co.za/files/Cms/General/d/10825/8b335fe7818a46d18a748ca88f492c9f.jpg',
# }, 
# {
# 	'title_article':"You",
# 	'urtToImage_article':'https://cdn.24.co.za/files/Cms/General/d/10825/8b335fe7818a46d18a748ca88f492c9f.jpg',
# },
# {
# 	'title_article':"Sestdien Latvijā pret Covid-19 vakcinēti tikai 125 cilvēki - TVNET",
# 	'urtToImage_article':'https://f7.pmo.ee/5V1H7UE5uNEsJflEI-0S84RWZNo=/1200x630/smart/nginx/o/2021/01/24/13592482t1hd95b.jpg',
# },
# {
# 	'title_article':"NASA's Upcoming Roman Space Telescope Could Image 100 Hubble Ultra Deep Fields at Once - SciTechDaily",
# 	'urtToImage_article':'https://f7.pmo.ee/5V1H7UE5uNEsJflEI-0S84RWZNo=/1200x630/smart/nginx/o/2021/01/24/13592482t1hd95b.jpg',
# },
# {
# 	'title_article':"You are a good person",
# }]

# print (newsClean(newsRows))


## Testing - TEXT 
# print(langEn("This may work"))
# print(langEn("Ein, zwei, drei, vier"))
# print(langEn("Sestdien Latvijā pret Covid-19 vakcinēti tikai 125 cilvēki - TVNET"))
# print(checkYoutube("https://www.youtube.com/watch?v=Dw1_kUMdOMo"))
# print(checkYoutube(""))
# print (lenCheck("yafafafafafaff"))
# print (checkProfanity("Yo"))


## Testing - IMAGE 
# print(checkImageSize("test.png", (438,588), "local"))
# print(checkImageSize("https://2.img-dpreview.com/files/p/TS1200x900~sample_galleries/1934460454/2688612977.jpg", (438,588)))
# print (imageExists("https://2.img-dpreview.com/files/p/TS1200x900~sample_galleries/1934460454/2688612977.jpg"))
# print (imageExists("https://2.img-dpreview.com/files/p/TS1200x900~sample_galries/1934460454/2688612977.jpg")) #non existant image