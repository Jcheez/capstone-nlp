# Time series + DA for Social Media data
from enum import auto
from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
from pandas import Timestamp
import dash_daq as daq


def create_social(filename):
    app = Dash(__name__)

    basePath = "./assets/inputs/"
    output_path = "./assets/outputs"

    # Variable that can be changed by user
    # comments_file_name = "standardized_covid_dataset_labelled"
    # posts_file_name = "standardized_ig_dataset_labelled"
    
    df = pd.read_excel(filename)

    # mandatory columns (standardized naming)
    # content_type: 'Post' or 'Comment'
    # id
    # text
    # time
    # label
    # likes: only for content_type = 'Post'
    # comments: only for content_type = 'Post'


    def process_timeseries_df(df):
        df['time'] = pd.to_datetime(df['time'])
        return df
    print(df.info())
    content_type = 'Posts' if df.iloc[0]['content_type'] == 'Posts' else 'Comments'

    df = process_timeseries_df(df)

    app.layout = html.Div([
        html.H1("Social Media Analysis", style={"textAlign": "center"}),
        html.P(f"File: {filename}",
            style={"textAlign": "center"}),

        html.Div([
            dcc.Markdown(f'Content Type: {content_type}')]),

        html.Div([
            dcc.Markdown('Topic Label(s)'),
            dcc.Dropdown(
                id="Topic Label",
                options=[{'label': l, 'value': l}
                        for l in df['label'].unique()],
                value=[],
                multi=True
            )], style={'width': '15%', 'paddingLeft': 30, 'display': 'inline-block'}),

        html.Div([dcc.Markdown('Aggregation Period'),
                dcc.Dropdown(
            id='Aggregation Period',
            options=[{'label': 'Yearly', 'value': 'Yearly'}, {'label': 'Monthly', 'value': 'Monthly'},
                    {'label': 'Daily', 'value': 'Daily'}],
            value='Monthly'
        )], style={'width': '15%', 'paddingLeft': 30, 'display': 'inline-block'}),

        html.Div([
            dcc.Markdown('Reaction Type *(only for Social Media Posts)*'),
            dcc.Dropdown(
                id='Reaction Type',
                options=[{'label': 'None', 'value': 'None'}, {
                    'label': 'Likes', 'value': 'Likes'}, {'label': 'Comments', 'value': 'Comments'}],
                value='None'
            )], style={'width': '20%', 'paddingLeft': 30, 'display': 'inline-block'}),

        html.Div([
            dcc.Markdown('Date Range'),
            dcc.DatePickerRange(
                id="Date Range",
                start_date=df["time"].min(),
                end_date=df["time"].max(),
                min_date_allowed=df["time"].min(),
                max_date_allowed=df["time"].max(),
                initial_visible_month=df["time"].min()
            )], style={'width': '20%', 'paddingLeft': 30, 'display': 'inline-block'}),

        html.Div([html.Br()]),

        html.Div([
            daq.BooleanSwitch(id='Proportion', on=False, label="Create Proportion",
                            labelPosition="top")
        ]),

        html.Div([html.Br()]),

        dcc.Loading(
            dcc.Graph(id='time_series')),
    ])


    @app.callback(
        Output('time_series', 'figure'),
        [Input('Topic Label', 'value'),
        Input('Aggregation Period', 'value'),
        Input('Reaction Type', 'value'),
        Input('Date Range', 'start_date'),
        Input('Date Range', 'end_date'),
        Input('Proportion', 'on')
        ]
    )
    def update_time_series_plot(topic_label, time_frame, reaction_type, start_date, end_date, proportion):

        timeSeries = df

        timeSeries = timeSeries.loc[timeSeries['time'].between(
            pd.to_datetime(start_date), pd.to_datetime(end_date))]

        # Filter by selected topic label(s)
        if (topic_label != []):
            timeSeries = timeSeries[timeSeries.label.isin(topic_label)]

        # Aggregate by chosen timeframe
        if time_frame == 'Yearly':
            timeSeries['trunc_time'] = timeSeries['time'].apply(lambda x: x.year)
        elif time_frame == 'Monthly':
            timeSeries['trunc_time'] = timeSeries['time'].apply(
                lambda x: Timestamp(x.year, x.month, 1))
        elif time_frame == 'Daily':
            timeSeries['trunc_time'] = timeSeries['time'].apply(
                lambda x: Timestamp(x.year, x.month, x.day))

        graphPlot = timeSeries[['label', 'trunc_time']].groupby(
            ['trunc_time', 'label']).size().reset_index().rename(columns={0: 'Frequency'})

        fig = px.area(graphPlot, x='trunc_time', y='Frequency', color='label',
                    labels={"trunc_time": "Date"}, title=f"Frequency of {content_type} over time")

        # Create proportion
        if (proportion == True):
            proportion_df = timeSeries[['label', 'trunc_time']
                                    ].value_counts().reset_index(name='count')
            # height = 1000 if len(topic_label) >= 4 or time_frame != 'Yearly' else 500
            proportion_df['Proportion'] = proportion_df['count'] / \
                proportion_df.groupby('trunc_time')['count'].transform('sum')
            fig = px.bar(proportion_df, y='Proportion', x='trunc_time', text='label', color='label',
                        title="Proportion of Topic Label over time")

        if (reaction_type != 'None' and content_type == 'Posts'):
            reaction_type_column = reaction_type.lower()
            count_reaction = timeSeries.groupby(['label', 'trunc_time'])[
                reaction_type_column].agg('sum').reset_index(name='Count')

            if (proportion == True):
                proportion_df = count_reaction
                proportion_df['Proportion'] = proportion_df['Count'] / \
                    proportion_df.groupby('trunc_time')['Count'].transform('sum')
                fig = px.bar(proportion_df, y='Proportion', x='trunc_time', text='label', color='label', labels={"trunc_time": "Date"},
                            title=f"Proportion of {reaction_type} for each Topic Label over time")
            else:
                fig = px.area(count_reaction, x='trunc_time', y='Count', color='label',
                            labels={"trunc_time": "Date"}, title=f"Count of {reaction_type} over time")

        # Set yearly intervals
        if time_frame == 'Yearly':
            fig.update_layout(
                xaxis=dict(
                    tickmode='linear',
                    dtick=1
                )
            )

        fig.update_layout(xaxis_title='Time', height=600)
        return fig


    app.run_server()


create_social("./assets/inputs/standardized_covid_dataset_labelled.xlsx")