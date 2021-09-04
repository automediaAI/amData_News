# amData_News
 - Pulls top news from various sources ie NewsAPI, Reddit etc
 - Uploads to CMS based on ask
 - See spec for more details  

 # How to works 
 - task.py runs main loop that goes through CMS news ask table 
 - this then calls respective news service to get data as dict
 - this data is passed through amLibrary fuctions to "clean" dict
 - Subservices tasks 
 -- All subservices send back data in standardized dict, so abstracts API level changes 
 -- all service like reddit, bing (ie except newsAPI) call mercury to pass news URL fetch news data in organized formatting 
 -- these services also call amLibrary_filters to check if data meets rules like length, profanity check etc 

 # Need to add 
 - Summarization service using amService_Summarizer 

 # Future 
 - Better unit tests 
 - TTS for text, with fillers 
