from dash import Dash, dcc, html, Input, Output
from os import path
from src.sentimentAnalysis.backend import run, run_absa
import pandas as pd
import plotly.express as px
import os

def create_sentiment(filepath):
    output_path = "./assets/outputs"
    file_name = os.path.basename(filepath).split(".")[0]

    if not path.isfile(f"{output_path}/{file_name}_result.csv"):
        run()
        run_absa()

    df = pd.read_csv(f"{output_path}/{file_name}_result.csv")
    absa_df = pd.read_csv(f"{output_path}/{file_name}_absa.csv")


    COLOR_MAPPING = {
        'joy': 'Yellow',
        'sadness': 'Blue',
        'fear': 'Purple',
        'anger': 'Red',
        'surprise': 'Brown',
        'love': 'Pink'
    }

    app = Dash(__name__)

    app.layout = html.Div([
        html.H1("Sentiment Analysis", style={"textAlign":"center"}),
        html.P(f"File: {file_name}", style={"textAlign":"center"}),
        html.Div([
            html.Div([
                html.P("Filter by Topic Label:", className="control_label"),
                dcc.Dropdown(
                    id="topic-label-dropdown",
                    options= [{'label' : l, 'value' : l} for l in df['label'].unique()],
                    value=[],
                    multi=True
                ),
                html.P("Filter by Aspect Label:", className="control_label"),   
                dcc.Dropdown(
                    id="aspect-label-dropdown",
                    options= [{'label' : l, 'value' : l} for l in absa_df['aspect_f'].dropna().unique()],
                    value=[],
                    multi=True
                ),
                html.P("Sort by Emotion:", className="control_label"),   
                dcc.Dropdown(
                    id="sort-emotion-dropdown",
                    options= [{'label' : l, 'value' : l} for l in df['emotion'].unique()],
                    value=None,
                ),
                html.P("Sort Direction:", className="control_label"),   
                dcc.RadioItems(
                    id="sort-direction-radio",
                    options= [{'label' : 'Ascending', 'value' : 'total ascending'}, {'label' : 'Descending', 'value' : 'total descending'}],
                    value='total ascending',
                ),
            ], className="left-col"),
            html.Div([
                html.Div([
                    html.Div([
                        html.P(id='numObservations', style={'fontSize': '48px', 'margin': 0}),
                        html.P(
                            "Observations", style={'fontSize': '12px', 'margin': 0}
                        )
                    ], className="mini_container"),
                    html.Div([
                        html.P(id='numLabels', style={'fontSize': '48px', 'margin': 0}),
                        html.P(
                            "Topic Labels", style={'fontSize': '12px', 'margin': 0}
                        )
                    ], className="mini_container"),
                    html.Div([
                        html.P(id='numAspectLabels', style={'fontSize': '48px', 'margin': 0}),
                        html.P(
                            "Aspect Labels", style={'fontSize': '12px', 'margin': 0}
                        )
                    ], className="mini_container"),
                    html.Div([
                        html.P(id='numAspectObservations', style={'fontSize': '48px', 'margin': 0}),
                        html.P(
                            "Aspect Observations", style={'fontSize': '12px', 'margin': 0}
                        )
                    ], className="mini_container")
                ], style={"display": "flex", "flex-direction": "row"}),
                html.Div(dcc.Graph(id="sentimentBar"), className="plots")
            ], className="right-col")
        ], style={"display": "flex", "flex-direction": "row"}),
        html.Div([
            html.Div(
                html.Div(
                    dcc.Graph(id="sentimentPie"), className="plots"
                ), className="gen-col"
            ),
            html.Div(
                html.Div(
                    dcc.Graph(id="absaBar"), className="plots"
                ), className="gen-col"
            ),
        ], style={"display": "flex", "flex-direction": "row"})
    ], style={"display": "flex", "flex-direction": "column"})


    # Callback for Emotion Bar plot
    @app.callback(
        Output("sentimentBar", "figure"),
        Input("topic-label-dropdown", "value"),
        Input("sort-emotion-dropdown", "value"),
        Input('sort-direction-radio', "value")
    )

    def update_bar_plot(filter, sortby, direction):
        dataset = df
        if len(filter) > 0:
            dataset = dataset[dataset['label'].isin(filter)]
        if sortby is not None:
            dataset = dataset[dataset['emotion'] == sortby]
        fig = px.histogram(
            dataset, 
            x='label', 
            y='emotion', 
            color='emotion', 
            barmode="group", 
            histfunc="count", 
            title="Emotion classification by Label",
            labels= {'label': 'Topic Labels', 'emotion': 'Emotions'},
            color_discrete_map=COLOR_MAPPING
        ).update_layout(title_x=0.5).update_xaxes(categoryorder=direction)
        return fig


    # Callback for ABSA bar plot
    @app.callback(
        Output("absaBar", "figure"),
        Input("topic-label-dropdown", "value"),
        Input("aspect-label-dropdown", "value"),
    )

    def update_absabar_plot(filter, aspect):
        dataset = absa_df
        if len(filter) > 0:
            dataset = dataset[dataset['label'].isin(filter)]
        if len(aspect) > 0:
            dataset = dataset[dataset['aspect_f'].isin(aspect)]
        fig = px.histogram(
            dataset, 
            x='aspect_f', 
            y='sentiment_f', 
            color='sentiment_f', 
            barmode="group", 
            histfunc="count",
            title="Aspect Based Emotional Classification",
            labels= {'aspect_f': 'Aspect Labels', 'sentiment_f': 'Sentiments'}
        ).update_layout(title_x=0.5)
        return fig


    # Callback for Emotion pie plot
    @app.callback(
        Output("sentimentPie", "figure"),
        Input("topic-label-dropdown", "value")
    )

    def update_pie_chart(filter):
        dataset = df
        dataset = dataset.groupby(by=["label", "emotion"]).count()
        dataset['emot'] = dataset.index.get_level_values(1)
        if len(filter) > 0:
            dataset = dataset.loc[(filter, slice(None)),:]
        fig = px.pie(
            dataset, 
            values="score", 
            names='emot',
            color='emot',
            title="Proportion of Emotion Classification by Label",
            color_discrete_map=COLOR_MAPPING
        ).update_layout(title_x=0.5, legend_title="Emotions")
        return fig


    # Callback for Aspect Label Dropdown
    @app.callback(
        Output("aspect-label-dropdown", "options"),
        Input("topic-label-dropdown", "value")
    )

    def update_aspect_label_dropdown(filter):
        dataset = absa_df
        if len(filter) > 0:
            dataset = dataset[dataset['label'].isin(filter)]
        return [{'label' : l, 'value' : l} for l in dataset['aspect_f'].dropna().unique()]


    # Callback to update DA

    @app.callback(
        Output("numObservations", 'children'),
        Output("numLabels", 'children'),
        Output("numAspectLabels", 'children'),
        Output("numAspectObservations", 'children'),
        Input("topic-label-dropdown", "value"),
        Input("aspect-label-dropdown", "value")
    )

    def update_descriptive_analytics(topics, aspects):
        dataset = df
        dataset_absa = absa_df
        if len(topics) > 0:
            dataset = dataset[dataset['label'].isin(topics)]
        if len(aspects) > 0:
            dataset_absa = dataset_absa[dataset_absa['aspect_f'].isin(aspects)]

        return len(dataset), len(dataset['label'].unique()), len(dataset_absa['aspect_f'].dropna().unique()), len(dataset_absa)


    app.run_server()