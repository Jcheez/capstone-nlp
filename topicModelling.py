# visit http://127.0.0.1:8050/ in your web browser.

from re import I
from dash import Dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import plotly.graph_objs as go
import dash_table
# from src.topicModelling.topic_modeling import top_n_words


basePath = "./assets/inputs/"
abs_name = "sensitised_IG_RnR_training_dataset" 

# top_n_words(abs_name)

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv(f"{basePath}{abs_name}_chart.csv")
df_sample = pd.read_csv(f"{basePath}{abs_name}_documents.csv")
df_cloud = pd.read_csv(f"{basePath}{abs_name}_wordcloud.csv")

def create_wordcloud(long_string):
    # # Import the wordcloud library
    # Create a WordCloud object
    wordcloud = WordCloud(background_color="white", max_words=5000,
                        contour_width=3, contour_color='steelblue')
    # Generate a word cloud
    wordcloud.generate(long_string)
    # Visualize the word cloud
    wordcloud.to_image()

app.layout = html.Div(children=[
    html.H1(children='Topic Modeling Summary'),
    
    html.Div(children='''
        A breakdown of different topic categories
    '''),

    dcc.Graph(
        id='example-graph',
        figure=go.Figure(
            data=[go.Pie(
                    # labels=df['Words'],
                    values=df['Size'],
                    customdata=df['Topic'],
                    marker_colors=px.colors.qualitative.Pastel,
                    hovertemplate="Relevant terms:<br><b>%{label}</b> <br>Count: %{value}<extra></extra>",
                    sort=False)  # to disable sorting for better understanding of chart
            ]),
        style={
            "paddingTop":"28px"
        }
    ),

    # dbc.Col([
    #         dbc.Card([
    #             dbc.CardBody([
    #                 dcc.Loading(
    #                     id="loading-2",
    #                     type="circle",
    #                     children=[
    #                         dcc.Graph(id='wordcloud', figure={},
    #                                   config={'displayModeBar': False})
    #                     ]
    #                 ),
    #                 html.Div(id='toggle_container', children=[
    #                     dash_table.DataTable(
    #                         style_data={
    #                             'whiteSpace': 'normal',
    #                             'height': 'auto'
    #                         },
    #                         # style_as_list_view=True,
    #                         id='sample_texts',
    #                         columns=[{"name": "Sample Text", "id": "text"}, {
    #                             "name": "Topic Proportion"}],
    #                         data=[{}],
    #                         page_current=0,
    #                         page_size=1,
    #                         page_action='custom',
    #                         style_cell={
    #                             'font_family': '"Nunito Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"'
    #                         },
    #                         style_cell_conditional=[{
    #                             'if': {'column_id': 'text'},
    #                             'textAlign': 'left',
    #                             'maxWidth': '70%',
    #                             'minWidth': '70%',
    #                             'width': '70%'
    #                         }, {
    #                             'if': {'column_id': 'topic_pred_score'},
    #                             'textAlign': 'center'
    #                         }],
    #                         css=[{
    #                             'selector': '.dash-spreadsheet td div',
    #                             'rule': '''
    #                                 max-height: 120px; min-height: 120px; height: 120px;
    #                                 display: block;
    #                                 overflow-y: auto;
    #                                 overflow-wrap: anywhere;
    #                             '''
    #                         }]
    #                     )], style={'display': 'none'})
    #             ])
    #         ])
    #     ], width=4, style={
    #         'paddingTop': '28px'
    #     })
])

if __name__ == '__main__':
    app.run_server(debug=True)