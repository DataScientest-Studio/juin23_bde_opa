import pytest

from opa.core import FinancialDataReader, Storage, StockMarketProvider


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
