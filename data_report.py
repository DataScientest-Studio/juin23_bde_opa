from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd


from storage import get_historical


dash_app = Dash(__name__)


def get_dataframe(ticker):
    data = get_historical(ticker)
    return pd.DataFrame(data)


@callback(Output("graph-content", "figure"), Input("dropdown-selection", "value"))
def update_graph(ticker):
    return px.line(get_dataframe(ticker), x="date", y="close")


dash_app.layout = html.Div(
    [
        html.Div(children="My First App with Data"),
        dcc.Dropdown(
            ["AAPL", "MSFT", "AMZN", "GOOG", "META"], "AAPL", id="dropdown-selection"
        ),
        dcc.Graph(id="graph-content"),
    ]
)

dash_app.run(host="0.0.0.0", debug=False)
