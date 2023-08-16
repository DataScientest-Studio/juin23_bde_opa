Dash seems to not be able to handle more than 1000 values when rangebreaks are enabled. This can be verified by changing the `get_dataframe` function from `data = [h.model_dump() for h in opa_storage.get_values(ticker, kind)]` to `data = [h.model_dump() for h in opa_storage.get_values(ticker, kind, 1001)]` (while setting 1000 will work).

2 solutions can be implemented.

Either chunk the dataframe by dates so that the number of values goes below 1000 :

```
n_values_by_chunk = 5
list_df = [df_ohlc[i:i+n_values_by_chunk] for i in range(0,df.shape[0],n_values_by_chunk)]
pd.concat(
    (d.groupby("ticker").agg({
        "close": "last", "volume": "sum", "open": "first", "high": "max", "low": "min"
    }).set_index(d.index[-1:]) for d in list_df)
)
```

... or simply disable rangebreaks if the number of values is above 1000.
