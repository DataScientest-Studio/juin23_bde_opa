# Historical data

This data is retrieved from the endpoint https://fmpcloud.io/api/v3/historical-price-full/AAPL

(See ["Daily Change and volume JSON"](https://fmpcloud.io/documentation#historicalStockData) for documentation)

An example of the full raw output can be found in `examples/fmpcloud_AAPL_history.json`. It is basically an array of such records, with field `date` iterating on all working days from today to the maximum history depth :

```
{
    "date": "2023-07-05",
    "open": 191.565,
    "high": 192.98,
    "low": 190.62,
    "close": 191.33,
    "adjClose": 191.330002,
    "volume": 46585657,
    "unadjustedVolume": 46358709,
    "change": -0.235,
    "changePercent": -0.12267,
    "vwap": 191.58,
    "label": "July 05, 23",
    "changeOverTime": -0.0012267
}
```

# Streaming data

This data is retrieved from the endpoint https://fmpcloud.io/api/v3/historical-chart/15min/AAPL

(See ["15 minute JSON"](https://fmpcloud.io/documentation#historicalStockData) for documentation)

An example of the full raw output can be found in `examples/fmpcloud_AAPL_15min.json`. It is basically an array of such records, with field `date` varying by increments of 15 minutes :

```
{
    "date": "2023-07-05 16:00:00",
    "open": 191.34,
    "low": 191.17,
    "high": 191.34,
    "close": 191.26,
    "volume": 2703704
}
```
