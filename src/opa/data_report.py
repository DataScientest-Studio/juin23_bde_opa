from loguru import logger
from dash import Dash, html, dcc, callback, Output, Input, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from opa import settings
from opa.core.financial_data import StockValueKind
from opa.storage import opa_storage


def get_dataframe(ticker: str, kind: StockValueKind) -> pd.DataFrame | None:
    data = [h.model_dump() for h in opa_storage.get_values(ticker, kind)]
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
            figure = go.Figure(
                go.Ohlc(
                    x=df.date,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                )
            )
            # Range slider is enabled by default for OHLC graphs even if the global
            # setting is set to False (see https://plotly.com/python/ohlc-charts/#ohlc-chart-without-rangeslider)
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
    dash_app.run(
        host=settings.data_report_host, port=settings.data_report_port, debug=True
    )
    logger.warning("Data report app finishing")
