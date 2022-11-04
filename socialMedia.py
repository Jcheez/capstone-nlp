# imports required for social media dashboard
from enum import auto
from dash import Dash, html, dcc, dash_table
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
from pandas import Timestamp
import dash_daq as daq

# creation of Social Media dashboard using Dash


def create_social(filename):
    app = Dash(__name__)

    # filename depends on the File Chosen
    df = pd.read_excel(filename)

    # social media dashboard can take in 2 types of content: either 'Post' or 'Comment'
    # this will be determined from the excel data taken in
    content_type = 'Posts' if df.iloc[0]['content_type'] == 'Post' else 'Comment'

    # process time series data

    def process_timeseries_df(df):
        df['time'] = pd.to_datetime(df['time'])
        return df
    df = process_timeseries_df(df)

    # manipulation of data to obtain trending topics
    trend_df = df
    trend_df['trunc_time'] = trend_df['time'].apply( lambda x: Timestamp(x.year, x.month, 1))
    trend_df = trend_df[['label', 'trunc_time']].value_counts().reset_index(name='count')
    trend_df['proportion'] = trend_df['count'] / trend_df.groupby('trunc_time')['count'].transform('sum')
    trend_df.sort_values(['trunc_time', 'label'],ascending=True, inplace=True)

    # calculations for proportion
    trend_df_proportion = pd.melt(
        trend_df, id_vars=['trunc_time', 'label'], value_vars=['proportion'])
    trend_df_proportion.drop(columns='variable', inplace=True)
    trend_df_proportion.rename(
        columns={'value': 'proportion'}, inplace=True)
    trend_df_proportion.set_index('trunc_time', inplace=True)
    trend_df_proportion['% Change in Proportion'] = (trend_df_proportion.groupby('label')['proportion']
                                                    .apply(pd.Series.pct_change))
    trend_df_proportion.set_index('label', append=True, inplace=True)

    # calculations for count
    trend_df_count = pd.melt(
        trend_df, id_vars=['trunc_time', 'label'], value_vars=['count'])
    trend_df_count.drop(columns='variable', inplace=True)
    trend_df_count.rename(columns={'value': 'count'}, inplace=True)
    trend_df_count.set_index('trunc_time', inplace=True)
    trend_df_count['Change in Count'] = trend_df_count.groupby('label')[
        'count'].diff()
    trend_df_count.set_index('label', append=True, inplace=True)

    # combined metrics (count & proportion) to determine trending topics
    trend_df_merged = pd.concat([trend_df_count, trend_df_proportion], axis=1)
    trend_df_merged.reset_index(inplace=True)
    default_prop_pct_change = 0
    default_count_change = 10
    trending = trend_df_merged[(trend_df_merged['% Change in Proportion'] > default_prop_pct_change) & (
        trend_df_merged['Change in Count'] > default_count_change)]
    trending.rename(
        columns={'trunc_time': 'Month', 'label': 'Trending Topic'}, inplace=True)


    # creating layout of Dash application
    app.layout = html.Div([
        html.H1("Social Media Analysis", style={"textAlign": "center"}),
        html.P(f"File: {filename}", style={"textAlign": "center"}),
        html.P(f'Content Type: {content_type}', style={"textAlign": "center"}),
        html.Div([
            html.Div([

                # visualisation filters 
                html.H1("Filters"),
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
                html.P("Reaction Type (only for Content Type: Posts)",
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

            # graph plot on count of posts/comment over time
            html.Div([
                dcc.Loading(dcc.Graph(id='time_series'))
            ], className="right-col")
        ], style={"display": "flex", "flex-direction": "row"}),
        html.Br(),

        # graph plot on proportion of topic labels over time
        dcc.Loading(dcc.Graph(id='proportion_graph')),
        html.Br(),

        # configurations for trending topics
        html.Div([
            html.Div([
                html.H3("Configuration for Trending Topics"),
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
                html.P("Metric 1: Increase in Number of Posts/Comments under that Topic from the previous month",
                       className="control_label"),
                daq.NumericInput(
                    id='count_change',
                    min=0,
                    max=trend_df_merged['Change in Count'].max(),
                    value=10
                ),
                html.P("Metric 2: Percentage Increase in Proportion of Posts/Comments under that Topic from the previous month",
                       className="control_label"),
                daq.NumericInput(
                    id='prop_pct_change',
                    min=0,
                    max=trend_df_merged['% Change in Proportion'].max()*100,
                    value=0
                ),
                html.P(
                    "Note: Users can set the metric to 0 if it should not be used to determine whether topics are trending"),
            ], className="left-col"),

            # table that displays the trending topics
            html.Div([
                html.H3("Trending Topics within Date Range",
                        style={"textAlign": "center"}),
                dash_table.DataTable(
                    id='trending_table',
                    columns= [{"name": "Month", "id": "Month"}, {"name": "Trending Topic", "id": "Trending Topic"}, {"name": "% Change in Proportion", "id": "% Change in Proportion"}, {"name": "Change in Count", "id": "Change in Count"}],
                    data=trending.to_dict('records'),
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

    # updating graph plot on count of posts/comment over time, based on the filters selected
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

        # Creating plot
        graphPlot = timeSeries[['label', 'trunc_time']].groupby(
            ['trunc_time', 'label']).size().reset_index().rename(columns={0: 'Number'})

        fig = px.line(graphPlot, x='trunc_time', y='Number', color='label',
                      labels={"trunc_time": "Date", "label": "Topic Label"}, title=f"Number of {content_type} over time")

        # Filter by reaction type (for Posts)
        if (reaction_type != 'None' and content_type == 'Posts'):
            reaction_type_column = reaction_type.lower()
            count_reaction = timeSeries.groupby(['label', 'trunc_time'])[
                reaction_type_column].agg('sum').reset_index(name='Number')

            fig = px.area(count_reaction, x='trunc_time', y='Number', color='label',
                          labels={"trunc_time": "Date", "label": "Topic Label"}, title=f"Number of {reaction_type} over time")

        # Set yearly intervals
        if time_frame == 'Yearly':
            fig.update_layout(
                xaxis=dict(
                    tickmode='linear',
                    dtick=1
                )
            )

        fig.update_layout(xaxis_title='Time', height=500, title_x=0.3)
        return fig

    # Updating graph plot on proportion of topic labels over time, based on filters selected
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

        proportion_df = timeSeries[['label', 'trunc_time']
                                   ].value_counts().reset_index(name='Number')
        proportion_df['Proportion'] = proportion_df['Number'] / \
            proportion_df.groupby('trunc_time')['Number'].transform('sum')
        fig = px.bar(proportion_df, y='Proportion', x='trunc_time', text='label', color='label', labels={"label": "Topic Label"},
                     title="Proportion of Topic Label over time")

        if (reaction_type != 'None' and content_type == 'Posts'):
            reaction_type_column = reaction_type.lower()
            count_reaction = timeSeries.groupby(['label', 'trunc_time'])[
                reaction_type_column].agg('sum').reset_index(name='Number')

            proportion_df = count_reaction
            proportion_df['Proportion'] = proportion_df['Number'] / \
                proportion_df.groupby('trunc_time')['Number'].transform('sum')
            fig = px.bar(proportion_df, y='Proportion', x='trunc_time', text='label', color='label', labels={"trunc_time": "Date", "label": "Topic Label"},
                         title=f"Proportion of {reaction_type} for each Topic Label over time")

        # Set yearly intervals
        if time_frame == 'Yearly':
            fig.update_layout(
                xaxis=dict(
                    tickmode='linear',
                    dtick=1
                )
            )

        fig.update_layout(xaxis_title='Time', height=700, title_x=0.5)
        return fig


    # Updating table of trending topics based on filters selected
    @app.callback(
        Output('trending_table', 'data'),
        [Input('Date Range for Trends', 'start_date'),
            Input('Date Range for Trends', 'end_date'),
            Input('count_change', 'value'),
            Input('prop_pct_change', 'value')]
    )
    def update_trending_topics_table(start_date, end_date, count_change, prop_pct_change):
        prop_pct_change = prop_pct_change/100

        # Filtering data based on the metrics selected
        trending = trend_df_merged[(trend_df_merged['% Change in Proportion'] >= prop_pct_change) & (
        trend_df_merged['Change in Count'] >= count_change)]
        trending.rename(
            columns={'trunc_time': 'Month', 'label': 'Trending Topic'}, inplace=True)


        # Filtering data based on date range selected
        updated_trending_topics = trending.loc[trending['Month'].between(
            pd.to_datetime(start_date), pd.to_datetime(end_date))]

        updated_trending_topics['Month'] = updated_trending_topics['Month'].apply(
            lambda x: x.strftime("%m/%Y"))

        return updated_trending_topics.to_dict('records')

    app.run_server()
