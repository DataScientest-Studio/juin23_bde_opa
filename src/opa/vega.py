from flask import Flask

import altair as alt
from vega_datasets import data
import pandas as pd

from opa.core import StockValueKind
from opa.storage import opa_storage

# Candlestick charts : https://altair-viz.github.io/gallery/candlestick_chart.html
# Ensure no breaks in graph from weekends/closing hours/... : https://stackoverflow.com/a/64312556
# A way to do "interval selection" (zoom onto the main graph by using a thumbnail)
# https://altair-viz.github.io/gallery/interval_selection.html

# Export chart to json : https://altair-viz.github.io/user_guide/saving_charts.html#json-format
# Vega embed : https://github.com/vega/vega-embed#directly-in-the-browser

# source = data.ohlc()
source = pd.DataFrame(
    [v.model_dump() for v in opa_storage.get_values("AAPL", StockValueKind.OHLC)]
)

open_close_color = alt.condition(
    "datum.open <= datum.close", alt.value("#06982d"), alt.value("#ae1325")
)

base = (
    alt.Chart(source)
    .encode(
        alt.X("yearmonthdatehoursminutes(date):O")
        .axis(format="%m/%d", labelAngle=-45)
        .title("Date in 2009"),
        color=open_close_color,
    )
    .properties(width=1000, height=500)
    .interactive(bind_y=False, bind_x=True)
)

rule = base.mark_rule().encode(
    alt.Y("low:Q").title("Price").scale(zero=False), alt.Y2("high:Q")
)

bar = base.mark_bar().encode(
    alt.Y("open:Q"),
    alt.Y2("close:Q"),
    tooltip=["yearmonthdatehoursminutes(date):T", "close:Q"],
)

graph = rule + bar


app = Flask(__name__)


@app.route("/")
def hello_world():
    return f"""

<!DOCTYPE html>
<html>
<head>
  <!-- Import Vega & Vega-Lite (does not have to be from CDN) -->
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <!-- Import vega-embed -->
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@5"></script>
</head>
<body>

<div id="vis"></div>

<script type="text/javascript">
  var spec = {graph.to_json()};
  vegaEmbed('#vis', spec).then(function(result) {{
    // Access the Vega view instance (https://vega.github.io/vega/docs/api/view/) as result.view
  }}).catch(console.error);
</script>
</body>
</html>
"""
