# Time series + DA for Social Media data
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Sentiment Analysis")
])

app.run_server(debug=True)