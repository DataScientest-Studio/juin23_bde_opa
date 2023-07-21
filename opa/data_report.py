from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd


from opa.storage import storage


def get_dataframe(ticker: str) -> pd.DataFrame:
    data = storage.get_historical(ticker)
    return pd.DataFrame(data)


@callback(Output("stock-evolution-graph", "figure"), Input("ticker-selector", "value"))
def update_graph(ticker: str):
    return px.line(get_dataframe(ticker), x="date", y="close")


@callback(
    Output("ticker-selector", "options"),
    Output("ticker-selector", "value"),
    Output("tickers-timer", "interval"),
    Input("tickers-timer", "n_intervals"),
)
def update_tickers_list(n):
    tickers = storage.get_all_tickers()
    return tickers, tickers[0] if tickers else None, 2000 if tickers else 200


if __name__ == "__main__":
    dash_app = Dash(__name__)

    dash_app.layout = html.Div(
        [
            dcc.Dropdown([], id="ticker-selector"),
            dcc.Interval("tickers-timer", 200, n_intervals=0),
            dcc.Graph(id="stock-evolution-graph"),
        ]
    )
    dash_app.run(debug=True)
