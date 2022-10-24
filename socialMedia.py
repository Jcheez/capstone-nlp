# Time series + DA for Social Media data
from enum import auto
from dash import Dash, html, dcc, dash_table
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
    df = pd.read_excel(filename)

    # mandatory columns (standardized naming)
    # content_type: 'Post' or 'Comment'
    # id
    # text
    # time
    # label
    # likes: only for content_type = 'Post'
    # comments: only for content_type = 'Post'

    content_type = 'Posts' if df.iloc[0]['content_type'] == 'Post' else 'Comment'

    def process_timeseries_df(df):
        df['time'] = pd.to_datetime(df['time'])
        return df

    df = process_timeseries_df(df)

    # for trending topics
    trend_df = df
    trend_df['trunc_time'] = trend_df['time'].apply(
        lambda x: Timestamp(x.year, x.month, 1))
    trend_df = trend_df[['label', 'trunc_time']
                        ].value_counts().reset_index(name='count')
    trend_df['proportion'] = trend_df['count'] / \
        trend_df.groupby('trunc_time')['count'].transform('sum')
    trend_df.sort_values(['trunc_time', 'label'],
                         ascending=True, inplace=True)

    # calculations for proportion
    trend_df_proportion = pd.melt(
        trend_df, id_vars=['trunc_time', 'label'], value_vars=['proportion'])
    trend_df_proportion.drop(columns='variable', inplace=True)
    trend_df_proportion.rename(
        columns={'value': 'proportion'}, inplace=True)
    trend_df_proportion.set_index('trunc_time', inplace=True)
    trend_df_proportion['proportion_pct_change'] = (trend_df_proportion.groupby('label')['proportion']
                                                    .apply(pd.Series.pct_change))
    trend_df_proportion.set_index('label', append=True, inplace=True)

    # calculations for count
    trend_df_count = pd.melt(
        trend_df, id_vars=['trunc_time', 'label'], value_vars=['count'])
    trend_df_count.drop(columns='variable', inplace=True)
    trend_df_count.rename(columns={'value': 'count'}, inplace=True)
    trend_df_count.set_index('trunc_time', inplace=True)
    trend_df_count['count_change'] = trend_df_count.groupby('label')[
        'count'].diff()
    trend_df_count['count_pct_change'] = (trend_df_count.groupby('label')['count']
                                          .apply(pd.Series.pct_change))
    trend_df_count.set_index('label', append=True, inplace=True)

    # combined
    trend_df_merged = pd.concat(
        [trend_df_count, trend_df_proportion], axis=1)
    trending = trend_df_merged[(trend_df_merged['proportion_pct_change'] > 0.5) & (trend_df_merged['count_change'] > 50)]
    trending.reset_index(inplace=True)
    trending_topics = trending[['trunc_time', 'label']]
    trending_topics.rename(
        columns={'trunc_time': 'Month', 'label': 'Trending Topic'}, inplace=True)

    app.layout = html.Div([
        html.H1("Social Media Analysis", style={"textAlign": "center"}),
        html.P(f"File: {filename}", style={"textAlign": "center"}),
        html.P(f'Content Type: {content_type}', style={"textAlign": "center"}),
        html.Div([
            html.Div([
                html.P("Topic Labels", className="control_label"),
                dcc.Dropdown(
                    id="Topic Label",
                    options=[{'label': l, 'value': l}
                             for l in df['label'].unique()],
                    value=[],
                    multi=True
                ),
                html.P("Aggregation Period", className="control_label"),
                dcc.Dropdown(
                    id='Aggregation Period',
                    options=[{'label': 'Yearly', 'value': 'Yearly'}, {'label': 'Monthly', 'value': 'Monthly'},
                             {'label': 'Daily', 'value': 'Daily'}],
                    value='Monthly'
                ),
                html.P("Reaction Type *(only for Content Type: Posts)*",
                       className="control_label"),
                dcc.Dropdown(
                    id='Reaction Type',
                    options=[{'label': 'None', 'value': 'None'}, {
                        'label': 'Likes', 'value': 'Likes'}, {'label': 'Comments', 'value': 'Comments'}],
                    value='None'
                ),
                html.P("Date Range", className="control_label"),
                dcc.DatePickerRange(
                    id="Date Range",
                    start_date=df["time"].min(),
                    end_date=df["time"].max(),
                    min_date_allowed=df["time"].min(),
                    max_date_allowed=df["time"].max(),
                    initial_visible_month=df["time"].min(),
                ),
            ], className="left-col"),
            html.Div([
                dcc.Loading(dcc.Graph(id='time_series'))
            ], className="right-col")
        ], style={"display": "flex", "flex-direction": "row"}),
        dcc.Loading(dcc.Graph(id='proportion_graph')),


        html.Div([
            html.Div([
                html.P("Date Range for Trending Topics",
                       className="control_label"),
                dcc.DatePickerRange(
                    id="Date Range for Trends",
                    start_date=df["time"].min(),
                    end_date=df["time"].max(),
                    min_date_allowed=df["time"].min(),
                    max_date_allowed=df["time"].max(),
                    initial_visible_month=df["time"].min(),
                ),
                html.P("Configure the following metrics to determine Trending Topics: ",
                       className="control_label"),
                html.P("Increase in Frequency by Month",
                       className="control_label"),
                daq.NumericInput(
                    id='count_change',
                    min=0,
                    max=trend_df_merged['count_change'].max(),
                    value=10
                ),
                html.P("Percentage Increase in Proportion by Month",
                       className="control_label"),
                daq.NumericInput(
                    id='prop_pct_change',
                    min=0,
                    max=trend_df_merged['proportion_pct_change'].max()*100,
                    value=50
                ),
            ], className="left-col"),
            html.Div([
                html.H3("Trending Topics within Date Range",
                        style={"textAlign": "center"}),
                dash_table.DataTable(
                    id='trending_table',
                    columns=[{"name": i, "id": i}
                             for i in trending_topics.columns],
                    data=trending_topics.to_dict('records'),
                    style_cell=dict(textAlign='left', padding='5px'),
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold'
                    },
                    style_data=dict(backgroundColor="lavender"),
                )
            ], className="right-col")
        ], style={"display": "flex", "flex-direction": "row"}),
    ])

    @ app.callback(
        Output('time_series', 'figure'),
        [Input('Topic Label', 'value'),
         Input('Aggregation Period', 'value'),
         Input('Reaction Type', 'value'),
         Input('Date Range', 'start_date'),
         Input('Date Range', 'end_date'),
         ]
    )
    def update_time_series_plot(topic_label, time_frame, reaction_type, start_date, end_date):

        timeSeries = df

        timeSeries = timeSeries.loc[timeSeries['time'].between(
            pd.to_datetime(start_date), pd.to_datetime(end_date))]

        # Filter by selected topic label(s)
        if (topic_label != []):
            timeSeries = timeSeries[timeSeries.label.isin(topic_label)]

        # Aggregate by chosen timeframe
        if time_frame == 'Yearly':
            timeSeries['trunc_time'] = timeSeries['time'].apply(
                lambda x: x.year)
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

        if (reaction_type != 'None' and content_type == 'Posts'):
            reaction_type_column = reaction_type.lower()
            count_reaction = timeSeries.groupby(['label', 'trunc_time'])[
                reaction_type_column].agg('sum').reset_index(name='Count')

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

        fig.update_layout(xaxis_title='Time', height=600, title_x=0.3)
        return fig

    @app.callback(
        Output('proportion_graph', 'figure'),
        [Input('Topic Label', 'value'),
         Input('Aggregation Period', 'value'),
         Input('Reaction Type', 'value'),
         Input('Date Range', 'start_date'),
         Input('Date Range', 'end_date'),
         ]
    )
    def update_proportion_plot(topic_label, time_frame, reaction_type, start_date, end_date):

        timeSeries = df

        timeSeries = timeSeries.loc[timeSeries['time'].between(
            pd.to_datetime(start_date), pd.to_datetime(end_date))]

        # Filter by selected topic label(s)
        if (topic_label != []):
            timeSeries = timeSeries[timeSeries.label.isin(topic_label)]

        # Aggregate by chosen timeframe
        if time_frame == 'Yearly':
            timeSeries['trunc_time'] = timeSeries['time'].apply(
                lambda x: x.year)
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

        proportion_df = timeSeries[['label', 'trunc_time']
                                   ].value_counts().reset_index(name='count')
        proportion_df['Proportion'] = proportion_df['count'] / \
            proportion_df.groupby('trunc_time')['count'].transform('sum')
        fig = px.bar(proportion_df, y='Proportion', x='trunc_time', text='label', color='label',
                     title="Proportion of Topic Label over time")

        if (reaction_type != 'None' and content_type == 'Posts'):
            reaction_type_column = reaction_type.lower()
            count_reaction = timeSeries.groupby(['label', 'trunc_time'])[
                reaction_type_column].agg('sum').reset_index(name='Count')

            proportion_df = count_reaction
            proportion_df['Proportion'] = proportion_df['Count'] / \
                proportion_df.groupby('trunc_time')['Count'].transform('sum')
            fig = px.bar(proportion_df, y='Proportion', x='trunc_time', text='label', color='label', labels={"trunc_time": "Date"},
                         title=f"Proportion of {reaction_type} for each Topic Label over time")

        # Set yearly intervals
        if time_frame == 'Yearly':
            fig.update_layout(
                xaxis=dict(
                    tickmode='linear',
                    dtick=1
                )
            )

        fig.update_layout(xaxis_title='Time', height=1000, title_x=0.5)
        return fig

    @app.callback(
        Output('trending_table', 'data'),
        [Input('Date Range for Trends', 'start_date'),
            Input('Date Range for Trends', 'end_date'),
            Input('count_change', 'value'),
            Input('prop_pct_change', 'value')]
    )
    def update_trending_topics_table(start_date, end_date, count_change, prop_pct_change):
        prop_pct_change = prop_pct_change/100
        trending = trend_df_merged[(trend_df_merged['proportion_pct_change'] >= prop_pct_change) & (trend_df_merged['count_change'] >= count_change)]
        trending.reset_index(inplace=True)
        trending_topics = trending[['trunc_time', 'label']]
        trending_topics.rename(
            columns={'trunc_time': 'Month', 'label': 'Trending Topic'}, inplace=True)

        updated_trending_topics = trending_topics.loc[trending_topics['Month'].between(
            pd.to_datetime(start_date), pd.to_datetime(end_date))]

        return updated_trending_topics.to_dict('records')

    app.run_server()
