import pandas as pd
from transformers.pipelines import pipeline
from pyabsa import ATEPCCheckpointManager
import nltk
from nltk.tokenize import TweetTokenizer
from nltk.stem import WordNetLemmatizer
import re

nltk.download('wordnet')
nltk.download('omw-1.4')
input_path = "./assets/inputs"
output_path = "./assets/outputs/sentiment_analysis"

def clean(text):
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True)
    lemmatizer = WordNetLemmatizer()
    tokenised = tokenizer.tokenize(text) # Tokenise text and replace contractions
    tokenised = list(filter(lambda x: not (bool(re.match("\B\#\S+ |\B\#\S+", x) or bool(re.match("[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+", x)) or bool(re.match("(?:https?|ftp):\/\/[\w\/\-?=%.]+\.[\w\/\-&?=%.]+", x)) or bool(re.match("(?:https ?|ftp):\/\/[\w\/\-?=%.]+\.[\w\/\-&?=%.]+", x)))), tokenised)) # remove hashtags
    tokenised = list(filter(lambda x: x.isalpha(), tokenizer.tokenize(" ".join(tokenised)))) # keep only alphabets
    lemmatized = [lemmatizer.lemmatize(token) for token in tokenizer.tokenize(" ".join(tokenised))] # lemmatized
    return " ".join(lemmatized)


def run(file_name):
    df = pd.read_excel(f"{input_path}/{file_name}.xlsx")
    classifier = pipeline("sentiment-analysis", model='bhadresh-savani/distilbert-base-uncased-emotion', truncation=True)
    
    df['emotional_analysis'] = df['text'].apply(lambda text: classifier(text)[0])
    df['emotion'] = df['emotional_analysis'].apply(lambda combined: combined['label'])
    df['score'] = df['emotional_analysis'].apply(lambda combined: combined['score'])

    df.to_csv(f"{output_path}/{file_name}_result.csv")


def run_absa(file_name):
    df = pd.read_csv(f"{output_path}/{file_name}_result.csv")
    df['processed_text'] = df['text'].apply(lambda x: clean(x))
    extractor = ATEPCCheckpointManager.get_aspect_extractor(checkpoint='english')
    res = extractor.extract_aspect(inference_source=df['processed_text'].tolist(), pred_sentiment=True,save_result=False, print_result=False)

    df['aspects'] = list(map(lambda x: x['aspect'], res))
    
    out = []
    for _, row in df.iterrows():
        if len(row['aspects']):
            for item in range(len(row['aspects'])):
                row['aspect_f'] = row['aspects'][item]
                out += [row.copy()]
        else:
            out += [row.copy()]

    pd.DataFrame(out).to_csv(f"{output_path}/{file_name}_absa.csv")