#####################
#### DEPRECATED SERVICE ##########
##### now using ChatGPT instead ########
################################

import json

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
tokenizer = AutoTokenizer.from_pretrained('facebook/bart-large-cnn')
model = AutoModelForSeq2SeqLM.from_pretrained('facebook/bart-large-cnn')
summarizer = pipeline('summarization', model=model, tokenizer=tokenizer)

###### Call Summarization pipeline and get data ######
def summarization_caller(article_in):
	# print(article_in)
	default_summary = summarizer(article_in, truncation=True)
	# long_summary = summarizer(news_item['text_article'], max_length=330, min_length=100, truncation=False)
	# short_summary = summarizer(news_item['text_article'], max_length=50, min_length=10, truncation=False)
	# return {'default_summary': default_summary[0]['summary_text'],
	#         'long_summary': long_summary[0]['summary_text'],
	#         'short_summary': short_summary[0]['summary_text']}
	# return default_summary Original, gives a list
	return default_summary[0]["summary_text"] #Just text


def summmary_ChatGPT(text):

	# Preprocess the text
	preprocessed_text = preprocess_text(text)
	# Join preprocessed text back into a string
	preprocessed_text_str = ' '.join(preprocessed_text)

	# Summarize the text
	summary = summarize_with_gpt(preprocessed_text_str)

	# Perform NER
	named_entities = perform_ner(preprocessed_text_str)


## Testing 
summary = summarization_caller("""When Sebastian Thrun started working on self-driving cars at Google in 2007,
    few people outside of the company took him seriously. “I can tell you very senior 
    CEOs of major American car companies would shake my hand and turn away because I 
    wasn’t worth talking to,” said Thrun, now the co-founder and CEO of online higher 
    education startup Udacity, in an interview with Recode earlier this week.

    The Mona Lisa and the Statue of David were on display in the MOMA New York.

    COVID-19 is a devastating virus currently ravaging the world.
    
    A little less than a decade later, dozens of self-driving startups have cropped up 
    while automakers around the world clamor, wallet in hand, to secure their place in 
    the fast-moving world of fully automated transportation.""")

print("Summary:", summary)