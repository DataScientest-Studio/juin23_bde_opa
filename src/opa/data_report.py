from dataclasses import dataclass

from loguru import logger
from dash import Dash, html, dcc, callback, Output, Input, no_update
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from opa import settings
from opa.core.financial_data import StockValueKind
from opa.http_methods import get_json_data


@dataclass
class Api:
    host: str
    port: int

    def get_stock_values(
        self, ticker: str, kind: StockValueKind, limit: int = None
    ) -> list[dict]:
        params = dict(kind=kind.value)
        if limit is not None:
            params |= dict(limit=limit)

        return get_json_data(self.endpoint(ticker), params=params)

    def all_tickers(self) -> list[str]:
        return get_json_data(self.endpoint("tickers"))

    def get_company_info(self, ticker: str) -> dict:
        return get_json_data(self.endpoint(f"company_infos/{ticker}"))

    def get_company_infos(self, tickers: list[str]) -> list[dict]:
        return get_json_data(
            self.endpoint("company_infos"), params=[("tickers", t) for t in tickers]
        )

    def endpoint(self, path: str) -> str:
        return f"http://{self.host}:{self.port}/{path}"


api = Api(settings.api_host, settings.api_port)


def get_dataframe(ticker: str, kind: StockValueKind) -> pd.DataFrame | None:
    if kind == StockValueKind.SIMPLE:
        # In the current setting, Dash does not display anything if more than 1000
        # values are displayed and the rangebreaks are enabled.
        limit = 1000
    elif kind == StockValueKind.OHLC:
        # Load as much values as possible
        limit = 0

    data = api.get_stock_values(ticker, kind, limit)
    return pd.DataFrame(data) if data else None


def add_range_selectors(figure, hour_break=False):
    breaks = [dict(bounds=["sat", "mon"])]
    if hour_break:
        # Seems like the first bound is exclusive and the
        # second one is inclusive, so we use 16.01 in order to display the stock
        # value at market close (16:00). It's not bulletproof though because
        # with that setting, the values at 16h00 and at 9h30 are almost superposed
        # on the X-axis of the graph.
        #
        # (this behaviour does not seem to be documented :
        # https://plotly.com/python/reference/layout/xaxis/#layout-xaxis-rangebreaks)
        breaks += [dict(bounds=[16.01, 9.5], pattern="hour")]

    return figure.update_xaxes(
        # Having the range slider visible makes it impossible to zoom along the y-axis,
        # which makes the plot very "flat" if the plotted value has a high amplitude overall
        # but locally fluctuates around a high value (e.g. a stock that started around 5$
        # and now values at around $100).
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
        # Rangebreaks seem to not work properly with very long series.
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
            figure = make_subplots(specs=[[{"secondary_y": True}]])
            figure.add_trace(
                go.Candlestick(
                    x=df.date,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name="Stock value",
                )
            )

            figure.add_trace(
                go.Bar(
                    x=df["date"],
                    y=df["volume"],
                    name="Volume",
                    marker_opacity=0.3,
                    marker_color=df.apply(
                        lambda v: "green" if v.close >= v.open else "red", axis=1
                    ),
                ),
                secondary_y=True,
            )

            # Range slider is enabled by default for OHLC/Candlestick graphs even if the global
            # setting is set to False (see https://plotly.com/python/candlestick-charts/#candlestick-without-rangeslider)
            figure.update(layout_xaxis_rangeslider_visible=False)

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
    tickers = api.all_tickers()
    infos = api.get_company_infos(tickers)

    options = [
        {
            "value": i["symbol"],
            "label": html.Span(
                [
                    html.Img(src=i["image"]),
                    html.Span(i["name"]),
                ],
                className="dropdown-option",
            ),
        }
        for i in sorted(infos.values(), key=lambda i: i["name"])
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
    info = api.get_company_info(ticker)
    return [
        html.H2(info["name"]),
        html.Img(src=info["image"]),
        html.P(info["description"]),
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
    dash_app.run(
        host=settings.data_report_host, port=settings.data_report_port, debug=True
    )
    logger.warning("Data report app finishing")
