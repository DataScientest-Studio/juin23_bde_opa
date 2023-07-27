from loguru import logger
from dash import Dash, html, dcc, callback, Output, Input, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from opa.core.financial_data import StockValueType
from opa.storage import opa_storage


def get_dataframe(ticker: str, type_: StockValueType) -> pd.DataFrame:
    data = [h.model_dump() for h in opa_storage.get_values(ticker, type_)]
    return pd.DataFrame(data)


def add_range_selectors(figure, hour_break=False):
    breaks = [dict(bounds=["sat", "sun"])]
    if hour_break:
        breaks += [dict(bounds=[16, 9.5], pattern="hour")]

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
        rangebreaks=breaks,
    )


def set_transparent_background(figure):
    return figure.update_layout(paper_bgcolor="hsla(0,0%,0%,0%)")


@callback(
    Output("stock-evolution-graph", "figure"),
    Input("ticker-selector", "value"),
    Input("type-selector", "value"),
)
def update_graph(ticker: str, type_str: str):
    type_ = StockValueType(type_str)
    df = get_dataframe(ticker, type_)
    df["rolling_close_3"] = df[["close"]][::-1].rolling(window=3).mean()[::-1]
    df["rolling_close_7"] = df[["close"]][::-1].rolling(window=7).mean()[::-1]

    figure = None
    match type_:
        case StockValueType.HISTORICAL:
            figure = go.Figure([
                go.Scatter(
                    x=df.date,
                    y=df.close,
                    mode='markers',
                    marker=dict(color='black', size=2),
                    showlegend=True
                ),
                go.Scatter(
                    x=df.date,
                    y=df.rolling_close_3,
                    mode='lines',
                    line=dict(color='red', width=1),
                    showlegend=True
                ),
                go.Scatter(
                    x=df.date,
                    y=df.rolling_close_7,
                    mode='lines',
                    line=dict(color='blue',width=1),
                    showlegend=True
                )
            ])

        case StockValueType.STREAMING:
            figure = go.Figure(
                go.Ohlc(
                    x=df.date,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                )
            )

    return set_transparent_background(
        add_range_selectors(figure, type_ == StockValueType.STREAMING)
    )


@callback(
    Output("ticker-selector", "options"),
    Output("ticker-selector", "value"),
    Input("tickers-refresh", "n_clicks"),
    Input("ticker-selector", "value"),
)
def refresh_tickers_list(n, current_ticker):
    tickers = opa_storage.get_all_tickers()
    infos = opa_storage.get_company_infos(tickers)

    options = [
        {
            "value": i.symbol,
            "label": html.Span(
                [
                    html.Img(src=i.image),
                    html.Span(i.name),
                ],
                className="dropdown-option",
            ),
        }
        for i in sorted(infos.values(), key=lambda i: i.name)
    ]

    new_selected_value = None
    if current_ticker:
        new_selected_value = no_update
    elif tickers:
        new_selected_value = options[0]["value"]

    return options, new_selected_value


@callback(
    Output("company-info", "children"),
    Input("ticker-selector", "value"),
)
def update_company_info(ticker: str):
    info = opa_storage.get_company_infos([ticker])[ticker]
    return [
        html.H2(info.name),
        html.Img(src=info.image),
        html.P(info.description),
    ]


if __name__ == "__main__":
    logger.info("Data report app starting up...")
    dash_app = Dash(__name__)

    dash_app.layout = html.Main(
        [
            dcc.Dropdown([], id="ticker-selector"),
            html.Div(id="company-info"),
            html.Button("Refresh tickers list", id="tickers-refresh"),
            dcc.Dropdown(
                [t.value for t in StockValueType],
                StockValueType.HISTORICAL.value,
                id="type-selector",
            ),
            dcc.Graph(id="stock-evolution-graph"),
        ]
    )
    dash_app.run(debug=True)
    logger.warning("Data report app finishing")
