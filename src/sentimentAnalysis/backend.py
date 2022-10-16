import pandas as pd
from transformers.pipelines import pipeline
from pyabsa import ATEPCCheckpointManager

input_path = "./assets/inputs"
output_path = "./assets/outputs"
file_name = "sensitised_covid_narrative_dataset_labelled"

def run():
    df = pd.read_excel(f"{input_path}/{file_name}.xlsx")
    classifier = pipeline("sentiment-analysis", model='bhadresh-savani/distilbert-base-uncased-emotion', truncation=True)
    
    df['emotional_analysis'] = df['text'].apply(lambda text: classifier(text)[0])
    df['emotion'] = df['emotional_analysis'].apply(lambda combined: combined['label'])
    df['score'] = df['emotional_analysis'].apply(lambda combined: combined['score'])

    df.to_csv(f"{output_path}/{file_name}_result.csv")


def run_absa():
    df = pd.read_excel(f"{input_path}/{file_name}.xlsx")
    extractor = ATEPCCheckpointManager.get_aspect_extractor(checkpoint='english')
    res = extractor.extract_aspect(inference_source=df['text'].tolist(), pred_sentiment=True,save_result=False, print_result=False)

    df['aspects'] = list(map(lambda x: x['aspect'], res))
    df['sentiments'] = list(map(lambda x: x['sentiment'], res))
    
    out = []
    for _, row in df.iterrows():
        if len(row['aspects']):
            for item in range(len(row['aspects'])):
                row['aspect_f'] = row['aspects'][item]
                row['sentiment_f'] = row['sentiments'][item]
                out += [row.copy()]
        else:
            out += [row.copy()]

    pd.DataFrame(out).to_csv(f"{output_path}/{file_name}_absa.csv")
