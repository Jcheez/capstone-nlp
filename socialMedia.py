# Time series + DA for Social Media data
from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
from pandas import Timestamp

app = Dash(__name__)

basePath = "./assets/inputs/"

# content type = comments
comments_path = "sensitised_covid_narrative_dataset_labelled" 
posts_path = "sensitised_IG_RnR_datasets_SingBert_labelled"

df_comments = pd.read_csv(f"{basePath}{comments_path}.csv") # mandatory columns (standardized naming): time, label
df_posts = pd.read_csv(f"{basePath}{posts_path}.csv") # mandatory columns (standardized naming): time, label

def process_timeseries_df(df, content_type):
  if (content_type == 'post'):
    df['time'] = pd.to_datetime(df['time'])
    df = df.rename(columns = {'text_label': 'label'})
    timeSeries = df
  else: # content_type == 'comment'
    df['comment_time'] = pd.to_datetime(df['comment_time'])
    timeSeries = df.rename(columns = {'comment_time':'time'})
  return timeSeries

df_comments = process_timeseries_df(df_comments, 'comment')
df_posts = process_timeseries_df(df_posts, 'post')


app.layout = html.Div([
    html.H1("Social Media Analysis"),
    dcc.Markdown("**Post/Comment Frequency Over Time**",style={'color': 'black', 'fontSize': 25,'textAlign': 'center'}),

    html.Div([dcc.Markdown('Aggregation Period'),
        dcc.Dropdown(
            id='Aggregation Period',
            options=[{'label': 'Yearly', 'value': 'Yearly'},{'label': 'Monthly', 'value': 'Monthly'},
                    {'label': 'Daily', 'value': 'Daily'}, {'label': 'No Aggregation', 'value': 'No Aggregation'}],
            value='Monthly'
        )], style={'width':'30%', 'display':'inline-block'}),

    html.Div([
        dcc.Markdown('Content Type'),
        dcc.Dropdown(
            id='Content Type',
            options=[{'label': 'Posts', 'value': 'Posts'},{'label': 'Comments', 'value': 'Comments'}],
            value='Posts'
        )], style={'width':'30%', 'paddingLeft':50, 'display':'inline-block'}),

    html.Div([
        dcc.Markdown('Reaction Type'),
        dcc.Dropdown(
            id='Reaction Type',
            options=[{'label': 'None', 'value': 'None'},{'label': 'Likes', 'value': 'Likes'},{'label': 'Comments', 'value': 'Comments'}],
            value='None'
        )], style={'width':'30%', 'paddingLeft':50, 'display':'inline-block'}),

    dcc.Loading(
        dcc.Graph(id = 'monthly_time_series'))

])

@app.callback(
    Output('monthly_time_series', 'figure'),
    [Input('Content Type', 'value'),
    Input('Aggregation Period', 'value'),
    Input('Reaction Type', 'value'),
    # Input('selected_label', 'value'),
    ]
    )


def update_time_series_plot(content_type, time_frame, reaction_type):

    # no user input for CSV files yet. df is hardcoded file path
    timeSeries = df_posts # default is df for posts
    if content_type == 'Comments':
        timeSeries = df_comments

    # #Filter by selected label
    # if label != 'all':
    #   timeSeries = timeSeries[timeSeries['label'] == label]

    #Aggregate by chosen timeframe
    if time_frame == 'Yearly':
        timeSeries['trunc_time'] = timeSeries['time'].apply(lambda x:x.year)
    elif time_frame == 'Monthly':
        timeSeries['trunc_time'] = timeSeries['time'].apply(lambda x:Timestamp(x.year, x.month, 1))
    elif time_frame == 'Daily':
        timeSeries['trunc_time'] = timeSeries['time'].apply(lambda x:Timestamp(x.year, x.month, x.day))
    elif time_frame == 'No Aggregation':
        timeSeries['trunc_time'] = timeSeries['time'].apply(lambda x:Timestamp(x.year, x.month, x.day, x.hour, x.minute))

    graphPlot = timeSeries[['label', 'trunc_time']].groupby(['trunc_time', 'label']).size().reset_index().rename(columns = {0:'Frequency'})
    
    if (reaction_type != 'None'):
        reaction_type_column = reaction_type.lower()
        print(reaction_type_column)
        graphPlot = timeSeries[['label', 'trunc_time', reaction_type_column]].groupby(['trunc_time', 'label', reaction_type_column]).size().reset_index().rename(columns = {0:'Frequency'})


    #Set to daily aggregation if there is only 1 time point
    if len(graphPlot) == 1:
        timeSeries['trunc_time'] = timeSeries['time'].apply(lambda x:Timestamp(x.year, x.month, x.day))
        graphPlot = timeSeries[['label', 'trunc_time']].groupby(['trunc_time', 'label']).size().reset_index().rename(columns = {0:'Frequency'})


    fig = px.area(graphPlot, x='trunc_time', y='Frequency', color = 'label',
        labels = {"trunc_time":"Date"})
    
    #Set yearly intervals
    if time_frame == 'Yearly':
        fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            dtick = 1
        )
    )

    fig.update_layout(yaxis_title = 'Frequency (Summed Across All Labels)')
    return fig

app.run_server(debug=True)

