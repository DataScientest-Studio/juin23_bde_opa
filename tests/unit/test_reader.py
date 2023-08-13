import pytest

from opa.core import FinancialDataReader, Storage, StockMarketProvider


@pytest.fixture
def provider(mocker):
    mocker.patch.multiple(StockMarketProvider, __abstractmethods__=set())
    return StockMarketProvider()


@pytest.fixture
def storage(mocker):
    mocker.patch.multiple(Storage, __abstractmethods__=set())
    return Storage()


@pytest.fixture
def reader(provider, storage):
    return FinancialDataReader(provider, storage)


class TestReader:
    def test_import_company_info(
        self, mocker, provider, storage, reader, company_infos
    ):
        mocker.patch.object(provider, "get_company_info", autospec=True)
        provider.get_company_info.return_value = company_infos
        mocker.patch.object(storage, "insert_company_infos", autospec=True)

        tickers = [c.symbol for c in company_infos]
        reader.import_company_info(tickers)

        provider.get_company_info.assert_called_once_with(tickers)
        storage.insert_company_infos.assert_called_once_with(company_infos)
