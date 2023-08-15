import pytest

from opa.core import (
    FinancialDataReader,
    Storage,
    StockMarketProvider,
    StockCollectionStats,
)
from tests.fixtures import fake_ticker


@pytest.fixture
def provider(mocker):
    mocker.patch.multiple(StockMarketProvider, __abstractmethods__=set())
    provider = StockMarketProvider()

    for method in ["get_stock_values", "get_company_info"]:
        mocker.patch.object(provider, method, autospec=True)

    return provider


@pytest.fixture
def storage(mocker):
    mocker.patch.multiple(Storage, __abstractmethods__=set())
    storage = Storage()

    for method in [
        "insert_values",
        "get_values",
        "get_all_tickers",
        "insert_company_infos",
        "get_company_infos",
        "get_stats",
    ]:
        mocker.patch.object(storage, method, autospec=True)

    return storage


@pytest.fixture
def reader(provider, storage):
    return FinancialDataReader(provider, storage)


class TestImportCompanyInfo:
    @pytest.fixture
    def provider_for_company_infos(self, provider, company_infos):
        provider.get_company_info.return_value = company_infos
        return provider

    def test_import_company_info(
        self, provider_for_company_infos, storage, reader, company_infos
    ):
        tickers = [c.symbol for c in company_infos]
        reader.import_company_info(tickers)

        provider_for_company_infos.get_company_info.assert_called_once_with(tickers)
        storage.insert_company_infos.assert_called_once_with(company_infos)


class TestImportStockValues:
    @pytest.fixture
    def storage_empty(self, storage):
        storage.get_stats.return_value = {}
        return storage

    @pytest.fixture
    def tickers(self):
        return [fake_ticker() for _ in range(5)]

    @pytest.fixture
    def storage_with_all_data(self, storage, tickers, stock_values_serie):
        storage.get_stats.return_value = {
            t: StockCollectionStats(
                latest=max((v.date for v in stock_values_serie)),
                oldest=min((v.date for v in stock_values_serie)),
                count=len(stock_values_serie),
            )
            for t in tickers
        }
        return storage

    @pytest.fixture
    def provider_for_stock_values(self, provider, stock_values_serie):
        provider.get_stock_values.return_value = stock_values_serie
        return provider

    def test_no_stored_data(
        self,
        tickers,
        provider_for_stock_values,
        storage_empty,
        reader,
        stock_value_kind,
        stock_value_serie_granularity,
        stock_values_serie,
    ):
        reader.import_stock_values(
            tickers, stock_value_kind, stock_value_serie_granularity
        )

        provider_for_stock_values.get_stock_values.assert_called()

        called_tickers = []
        for args in provider_for_stock_values.get_stock_values.call_args_list:
            called_tickers.append(args.args[0])
            type_ = args.args[1]
            assert type_ == stock_value_kind
        assert sorted(tickers) == sorted(called_tickers)

        storage_empty.insert_values.assert_called_once()
        assert sorted(
            storage_empty.insert_values.call_args.args[0], key=lambda v: v.date
        ) == sorted(stock_values_serie * 5, key=lambda v: v.date)

    def test_all_stored_data(
        self,
        tickers,
        provider_for_stock_values,
        storage_with_all_data,
        reader,
        stock_value_kind,
        stock_value_serie_granularity,
    ):
        reader.import_stock_values(
            tickers, stock_value_kind, stock_value_serie_granularity
        )

        provider_for_stock_values.get_stock_values.assert_called()

        called_tickers = []
        for args in provider_for_stock_values.get_stock_values.call_args_list:
            called_tickers.append(args.args[0])
            type_ = args.args[1]
            assert type_ == stock_value_kind
        assert sorted(tickers) == sorted(called_tickers)

        storage_with_all_data.insert_values.assert_not_called()
