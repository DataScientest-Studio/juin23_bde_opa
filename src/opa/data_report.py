from loguru import logger
from dash import Dash, html, dcc, callback, Output, Input, no_update
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from opa.core.financial_data import StockValueKind
from opa.storage import opa_storage


def get_dataframe(ticker: str, kind: StockValueKind) -> pd.DataFrame | None:
    data = [h.model_dump() for h in opa_storage.get_values(ticker, kind)]
    return pd.DataFrame(data) if data else None


def add_range_selectors(figure, hour_break=False):
    breaks = [dict(bounds=["sat", "mon"])]
    if hour_break:
        breaks += [dict(bounds=[16, 9.5], pattern="hour")]

    return figure.update_xaxes(
        rangeslider_visible=False,
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
    Output("errors", "children"),
    Output("errors", "className"),
    Input("ticker-selector", "value"),
    Input("type-selector", "value"),
)
def update_graph(ticker: str, type_str: str):
    kind = StockValueKind(type_str)
    df = get_dataframe(ticker, kind)

    if df is None:
        return (
            no_update,
            f"Sorry, no {type_str} values could be found for {ticker}",
            "active",
        )

    figure = None
    match kind:
        case StockValueKind.SIMPLE:
            figure = px.line(df, x="date", y="close")

        case StockValueKind.OHLC:
            figure = make_subplots(rows=2, cols=1, shared_xaxes=True)
            figure.add_trace(
                go.Ohlc(
                    x=df.date,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                ),
                row=1,
                col=1,
            )
            figure.add_trace(
                go.Bar(
                    x=df.date,
                    y=df.volume,
                    marker_color=df.apply(
                        lambda v: "green" if v.close >= v.open else "red", axis=1
                    ),
                ),
                row=2,
                col=1,
            )

    return (
        set_transparent_background(
            add_range_selectors(figure, kind == StockValueKind.OHLC)
        ),
        "",
        "",
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
                [t.value for t in StockValueKind],
                StockValueKind.SIMPLE.value,
                id="type-selector",
            ),
            dcc.Graph(id="stock-evolution-graph", config={"scrollZoom": True}),
            html.Div(id="errors"),
        ]
    )
    dash_app.run(debug=True)
    logger.warning("Data report app finishing")
