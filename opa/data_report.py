from dash import Dash, html, dcc, callback, Output, Input, no_update
import plotly.express as px
import pandas as pd


from opa.core.financial_data import StockValueType
from opa.storage import storage


def get_dataframe(ticker: str, type_: StockValueType) -> pd.DataFrame:
    data = [h.model_dump() for h in storage.get_values(ticker, type_)]
    return pd.DataFrame(data)


def add_range_selectors(figure):
    return figure.update_xaxes(
        rangeslider_visible=True,
        rangeselector={
            "buttons": [
                dict(label="1m", count=1, step="month", stepmode="backward"),
                dict(label="6m", count=6, step="month", stepmode="backward"),
                dict(label="YTD", count=1, step="year", stepmode="todate"),
                dict(label="1y", count=1, step="year", stepmode="backward"),
                dict(step="all"),
            ]
        },
    )


@callback(Output("stock-evolution-graph", "figure"), Input("ticker-selector", "value"))
def update_graph(ticker: str):
    df = get_dataframe(ticker, StockValueType.HISTORICAL)
    figure = px.line(df, x="date", y="close")
    return add_range_selectors(figure)


@callback(
    Output("ticker-selector", "options"),
    Output("ticker-selector", "value"),
    Output("tickers-timer", "interval"),
    Input("tickers-timer", "n_intervals"),
    Input("ticker-selector", "value"),
)
def update_tickers_list(n, current_ticker):
    tickers = storage.get_all_tickers()

    new_selected_value = None
    if current_ticker:
        new_selected_value = no_update
    elif tickers:
        new_selected_value = tickers[0]

    return tickers, new_selected_value, 2000 if tickers else 200


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
