from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd


from opa.storage import storage


def get_dataframe(ticker: str) -> pd.DataFrame:
    data = storage.get_historical(ticker)
    return pd.DataFrame(data)


@callback(Output("graph-content", "figure"), Input("dropdown-selection", "value"))
def update_graph(ticker: str):
    return px.line(get_dataframe(ticker), x="date", y="close")


if __name__ == "__main__":
    dash_app = Dash(__name__)
    dash_app.layout = html.Div(
        [
            html.Div(children="My First App with Data"),
            dcc.Dropdown(
                ["AAPL", "MSFT", "AMZN", "GOOG", "META"],
                "AAPL",
                id="dropdown-selection",
            ),
            dcc.Graph(id="graph-content"),
        ]
    )
    dash_app.run(debug=False)
