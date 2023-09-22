from dataclasses import dataclass
from enum import Enum

from loguru import logger
from dash import Dash, html, dcc, callback, Output, Input, no_update
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from opa import settings
from opa.core.financial_data import StockValueKind
from opa.http_methods import get_json_data


nb_points_choices = [200, 500, 1_000, 2000, 5000, 10000, 0]


class CheckBoxValue(Enum):
    DISPLAY_SLIDER = "DISPLAY_SLIDER"

    @staticmethod
    def all_checked(checked_values: str | None):
        if checked_values is None:
            return []
        else:
            return [CheckBoxValue(v) for v in checked_values]


@dataclass
class Api:
    host: str
    port: int
    username: str
    password: str

    def get_stock_values(
        self, ticker: str, kind: StockValueKind, limit: int = None
    ) -> list[dict]:
        params = dict(kind=kind.value)
        if limit is not None:
            params |= dict(limit=limit)

        return self._do_request(ticker, params)

    def all_tickers(self) -> list[str]:
        return self._do_request("tickers")

    def get_company_info(self, ticker: str) -> dict:
        return self._do_request(f"company_infos/{ticker}")

    def get_company_infos(self, tickers: list[str]) -> list[dict]:
        return self._do_request("company_infos", [("tickers", t) for t in tickers])

    def _do_request(self, path: str, params: list | dict = []):
        endpoint = f"http://{self.host}:{self.port}/{path}"
        return get_json_data(
            endpoint, params=params, auth=(self.username, self.password)
        )


api = Api(
    settings.api_host,
    settings.api_port,
    settings.secrets.data_report_api_username,
    settings.secrets.data_report_api_password,
)


def get_dataframe(
    ticker: str, kind: StockValueKind, nb_points: int
) -> pd.DataFrame | None:
    data = api.get_stock_values(ticker, kind, nb_points)
    return pd.DataFrame(data) if data else None


def add_range_selectors(figure, display_slider, hour_break=False):
    breaks = [dict(bounds=["sat", "mon"])]
    if hour_break:
        # The behaviour of this setting is really not well documented
        # (see https://plotly.com/python/time-series/#hiding-nonbusiness-hours
        # or https://plotly.com/python/reference/layout/xaxis/#layout-xaxis-rangebreaks)
        #
        # The natural setting to use seems to be [16, 9.5], but.. Using that setting
        # hides the value produced at 16:00 every day (while the value produced at
        # 9:30 is properly displayed) ; it seems like the first bound is exclusive, and
        # the second is inclusive.
        #
        # Something like `[16.5, 9.5]`` produces a visible gap between the last value of
        # a day, and the first value of the next day. `[16.01, 9.5]`` displays both values
        # but they are almost superposed.
        #
        # Even though completely unlogical, `[16.01, 9.25]` kinda does the trick, and
        # displays both values without a noticeable gap in-between them.
        breaks += [dict(bounds=[16.01, 9.25], pattern="hour")]

    return figure.update_xaxes(
        # Having the range slider visible makes it impossible to zoom along the y-axis,
        # which makes the plot very "flat" if the plotted value has a high amplitude overall
        # but locally fluctuates around a high value (e.g. a stock that started around 5$
        # and now values at around $100).
        rangeslider_visible=display_slider,
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
    Input("ui-display-check", "value"),
    Input("nb-points-slider", "value"),
)
def update_graph(
    ticker: str, type_str: str, checked: list | None, nb_points_value: int
):
    checked = CheckBoxValue.all_checked(checked)
    display_slider = CheckBoxValue.DISPLAY_SLIDER in checked

    kind = StockValueKind(type_str)

    # For some reason, Dash will not display anything if more than 1000
    # values are displayed with "SIMPLE" values and the rangebreaks are enabled.
    # So choose those UI settings wisely.
    df = get_dataframe(ticker, kind, nb_points_choices[nb_points_value])

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
            add_range_selectors(figure, display_slider, kind == StockValueKind.OHLC)
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
    Output("company-image", "src"),
    Output("company-description", "children"),
    Input("ticker-selector", "value"),
)
def update_company_info(ticker: str):
    info = api.get_company_info(ticker)
    return info["image"], info["description"]


if __name__ == "__main__":
    logger.info("Data report app starting up...")
    dash_app = Dash(__name__)

    dash_app.layout = html.Main(
        [
            dcc.Dropdown([], id="ticker-selector"),
            dcc.Checklist(
                options=[
                    {"label": "Display slider", "value": CheckBoxValue.DISPLAY_SLIDER}
                ],
                id="ui-display-check",
            ),
            dcc.Slider(
                id="nb-points-slider",
                marks={idx: str(v) for idx, v in enumerate(nb_points_choices)},
                value=1,
                step=None,
            ),
            html.Img(id="company-image"),
            html.P(id="company-description"),
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
