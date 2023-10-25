##############################################
##############################################
##### Text Tokenizer Using NTLK ##############
### Being used for Summarizing for now #######
####################################
#### Created with ChatGPT Assistance #########
##############################################


import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Tokenize into words
    words = word_tokenize(text)
    return words
