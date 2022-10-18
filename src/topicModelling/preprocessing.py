import numpy as np
import pandas as pd
import re
import nltk
from nltk.tokenize import TweetTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import contractions
nltk.download('stopwords')
def df_to_dict(storage, cols):
  dct = {}
  for index, row in storage.iterrows():
    dct[row[cols[0]]] = row[cols[1]]
  return dct

emoji_dict_path = "./assets/static/emoji.xlsx"
emoticon_dict_path = "./assets/static/emoticons.xlsx"
nonenglish_dict_path = "./assets/static/nonenglish.xlsx" 

emojis = pd.read_excel(emoji_dict_path)
emojis_dict = df_to_dict(emojis, ['Emoji', 'Meaning'])

emoticons = pd.read_excel(emoticon_dict_path)
emoticons_dict = df_to_dict(emoticons, ['Emoticon', 'Meaning'])

nonenglish = pd.read_excel(nonenglish_dict_path)
nonenglish_dict = df_to_dict(nonenglish, ["Word", "Meaning"])

tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True)
lemmatizer = WordNetLemmatizer()
stop = set(stopwords.words('english'))

def clean(text):
  tokenised = tokenizer.tokenize(contractions.fix(text)) # Tokenise text and replace contractions
  tokenised = list(map(lambda x: x if x not in emojis_dict else emojis_dict[x], tokenised)) # replace emoji with text
  tokenised = list(map(lambda x: x if x not in emoticons_dict else emoticons_dict[x], tokenised)) # replace emoticon with text
  tokenised = list(filter(lambda x: not (bool(re.match("\B\#\S+ |\B\#\S+", x) or bool(re.match("[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+", x)) or bool(re.match("(?:https?|ftp):\/\/[\w\/\-?=%.]+\.[\w\/\-&?=%.]+", x)) or bool(re.match("(?:https ?|ftp):\/\/[\w\/\-?=%.]+\.[\w\/\-&?=%.]+", x)))), tokenised)) # remove hashtags
  tokenised = list(filter(lambda x: x.isalpha(), tokenizer.tokenize(" ".join(tokenised)))) # keep only alphabets
  tokenised = list(filter(lambda x: x not in stop, tokenised))

  cleaned = list(map(lambda x: x if x not in nonenglish_dict else nonenglish_dict[x], tokenised))
  return " ".join(cleaned)

