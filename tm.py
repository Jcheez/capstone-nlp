from re import I
from dash import Dash, dcc, html, dash_table
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import plotly.graph_objs as go
from io import BytesIO
import base64
import dash
from src.topicModelling.topic_modeling import create_topics
import os.path
from os import path
from dash.dependencies import Input, Output

basePath = "./assets/outputs/topic_modeling/"
file_name_piechart = 'sensitised_IG_RnR_training_dataset_chart'
file_name_wordcloud = 'sensitised_IG_RnR_training_dataset_wordcloud'

# Create Pie Chart for Topic Breakdown
df_piechart = pd.read_csv(f"{basePath}{file_name_piechart}.csv")
df_piechart['Words'] = df_piechart['Words'].str[1:-1]
piechart_fig = px.pie(df_piechart, values='Size', names='Words', color='Topic',
             )
piechart_fig.update_traces(textposition='inside', textinfo='percent', hovertemplate="Relevant terms:<br>%{label}</b> <br>Count: <b>%{value}<extra></extra>")
piechart_fig.update_layout(legend_title_text='Top Words for each Topic', legend=dict(
    xanchor="right",
    x=0.05,
    font=dict(
            size=15,
    ),
))

# Create Word Cloud
df_wordcloud = pd.read_csv(f"{basePath}{file_name_wordcloud}.csv")
df_wordcloud['Topic'].unique()
def plot_wordcloud(long_string):
    # # Import the wordcloud library
    # Create a WordCloud object
    wordcloud = WordCloud(background_color="white", max_words=5000,
                        contour_width=3, contour_color='steelblue', scale=1, collocations=True)
    # Generate a word cloud
    wordcloud.generate(long_string)
    # Visualize the word cloud
    return wordcloud.to_image()



app = Dash(__name__)
app.layout = html.Div([

    html.H1("Topic Modeling Summary", style={"textAlign": "center"}),
    html.P(f"File: {file_name_piechart}",
           style={"textAlign": "center"}),

    dcc.Markdown("**Topic Breakdown**",
                 style={'color': 'black', 'fontSize': 25, 'textAlign': 'center'}),

    dcc.Graph(
        id='Topic-breakdown',
        figure=piechart_fig
    ),

    html.Br(),
    html.Br(),

    dcc.Markdown("**Word Cloud**",
                 style={'color': 'black', 'fontSize': 25, 'textAlign': 'center'}),
    html.Div([
    dcc.Markdown('Word Cloud Topic'),
        dcc.Dropdown(
            id='Word Cloud Topic',
            options=[{'label': l+2, 'value': l}
                     for l in df_wordcloud['Topic'].unique()],
            value=-1
        )], style={'width': '15%', 'display': 'inline-block'}),

    html.Div([html.Br()]),

    html.Img(id='wordcloud', style={
                'height': '50%',
                'width': '50%',
            })], style={'textAlign': 'center'})

@app.callback(
    Output('wordcloud', 'src'),
    [Input('Word Cloud Topic', 'value'),
     ]
)
def make_image(wordcloud_topic):
    img = BytesIO()
    plot_wordcloud(df_wordcloud.iloc[wordcloud_topic]["Doc"]).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

app.run_server(debug=True)
