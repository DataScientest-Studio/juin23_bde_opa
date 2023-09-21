---
author: Julien Hervé
title: OPA project demonstration
date: September 26, 2023
---

# Introduction

## Some vocabulary

::: incremental

- *ticker* / *symbol* : a short identifer for a company stock (e.g. AAPL => Apple, MSFT => Microsoft, META => Meta)
- *OHLC* : "open", "high", "low", "close"
- *volume* : the number of stock values exchanged

:::

## Architecture

![Architecture overview](../images/graphs/architecture.png)

# If we only had the external API..

[demo]

::: incremental

* Slow
* API is limited (~250 hits/day)
* No custom querying (e.g. several tickers)

:::

# Getting external data into local storage

[demo]

::: incremental

* No more API limits
* Data can be queried in all ways

:::

# Adding an HTTP API

[demo]

[connect to [http://63.35.39.206:8000/docs](http://63.35.39.206:8000/docs)]

::: incremental

* Allows access to third-parties
* Extensible at will
* Secure

:::

# Data consumption : the dashboard

## Inspiration (1)

![Apple trending line](../images/AAPL_trend_line.png)

## Inspiration (2)

![Apple Candlesticks graph](../images/AAPL_candles.png)

## Demo

[demo]

[connect to [http://63.35.39.206:8050/](http://63.35.39.206:8050)]
