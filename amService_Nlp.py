import spacy

nlp = spacy.load("en_core_web_md")

ner_ban_list = [
    "PERCENT",
    "MONEY",
    "QUANTITY",
    "ORDINAL",
    "CARDINAL",
    "DATE"
]

###### Call spaCy and get Named Entities as keywords ######
###### This ignores some NERs which are specified    ######
###### in the hardcoded list above                   ######
def ner_caller(article_in):
    # print(article_in)
    return_list = []
    doc = nlp(article_in)
    for ent in doc.ents:
        # print(ent.text, ent.start_char, ent.end_char, ent.label_)
        if ent.label_ not in ner_ban_list and ent.text not in return_list:
            return_list.append(ent.text)
    return return_list # returns empty list if nothing found

x = ner_caller("""When Sebastian Thrun started working on self-driving cars at Google in 2007,
    few people outside of the company took him seriously. “I can tell you very senior 
    CEOs of major American car companies would shake my hand and turn away because I 
    wasn’t worth talking to,” said Thrun, now the co-founder and CEO of online higher 
    education startup Udacity, in an interview with Recode earlier this week.

    The Mona Lisa and the Statue of David were on display in the MOMA New York.

    COVID-19 is a devastating virus currently ravaging the world.
    
    A little less than a decade later, dozens of self-driving startups have cropped up 
    while automakers around the world clamor, wallet in hand, to secure their place in 
    the fast-moving world of fully automated transportation.""")
print(x)