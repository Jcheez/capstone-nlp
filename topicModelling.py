# visit http://127.0.0.1:8050/ in your web browser.

from re import I
from dash import Dash, dcc, html, dash_table
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import plotly.graph_objs as go
from io import BytesIO
import base64
# from src.topicModelling.topic_modeling import top_n_words
import dash
from src.topicModelling.topic_modeling import create_topics
import os.path
from os import path


def topic_model(filepath):
    basePath = "./assets/outputs/topic_modeling/"
    basename = os.path.basename(filepath).split(".")[0]

    if not path.isfile(f"{basePath}{basename}_chart.csv"):
        create_topics(filepath)

    df = pd.read_csv(f"{basePath}{basename}_chart.csv")
    df_sample = pd.read_csv(f"{basePath}{basename}_documents.csv")
    df_cloud = pd.read_csv(f"{basePath}{basename}_wordcloud.csv")
    df["Words"] = df["Words"].map(lambda x: x[1: -1].replace("'", ""))

    #Filter out all -1 topics
    df_outlier = df.loc[df["Topic"] == -1]
    df = df.loc[df["Topic"] != -1]

    df_sample_outlier = df_sample.loc[df_sample["Topic"] == -1]
    df_sample = df_sample.loc[df_sample["Topic"] != -1]

    df_cloud_outlier = df_cloud.loc[df_cloud["Topic"] == -1]
    df_cloud = df_cloud.loc[df_cloud["Topic"] != -1]

    def plot_wordcloud(long_string):
        # # Import the wordcloud library
        # Create a WordCloud object
        wordcloud = WordCloud(background_color="white", max_words=5000,
                            contour_width=3, contour_color='steelblue')
        # Generate a word cloud
        wordcloud.generate(long_string)
        # Visualize the word cloud
        return wordcloud.to_image()



    app = Dash(__name__)
    app.layout = html.Div(children=[
        html.H1(children='Topic Modeling Summary'),
        html.Div(children='''
            A breakdown of different topic categories
        '''),
        html.Br(),
        html.H2("Topic breakdown", style={"textAlign":"center"}),
        dcc.Graph(
            id='Topic-breakdown',
            figure=go.Figure(
                data=[go.Pie(
                        labels=df['Words'],
                        values=df['Size'],
                        customdata=df['Topic'],
                        marker_colors=px.colors.qualitative.Pastel,
                        hovertemplate="Relevant terms:<br><b>%{label}</b> <br>Count: %{value}<extra></extra>",
                        sort=False)  # to disable sorting for better understanding of chart
                ],
                layout={
                    "height":550
                }).update_layout(legend={
                            "yanchor": "bottom",
                            "y": -0.25,
                            "xanchor": "left",
                            "x": 0.05
                        }, margin=dict(t=0, b=0, l=0, r=0), font=dict(size=18)),
            style={
                "overflowX": "hidden",
            }
        ),

        html.Br(),
        html.Br(),

        html.Div(
            html.Img(id="wordcloud", style={
                "height":"40%",
                "width":"40%"
            }),
            style={
                "textAlign": "center",            
            }
        )
        

    ])


    @app.callback(dash.dependencies.Output('wordcloud', 'src'), [dash.dependencies.Input('wordcloud', 'id')])
    def make_image(b):
        img = BytesIO()
        plot_wordcloud(df_cloud.iloc[0]["Doc"]).save(img, format='PNG')
        return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


    if __name__ == '__main__':
        app.run_server(debug=True)