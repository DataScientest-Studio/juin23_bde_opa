import pytest
from faker import Faker
from datetime import timedelta

from opa.core import CompanyInfo, StockValue, StockValueType, StockCollectionStats
from opa.storage import opa_storage


fake = Faker()


def fake_value() -> float:
    return fake.pyfloat(right_digits=2, min_value=0.5, max_value=100.0)


@pytest.fixture(scope="function")
def db_wipeout():
    # This relies on knowledge of opa_storage implementation but it's good enough
    # in this scope
    for c in opa_storage.collections.values():
        # We delete all the data in each collection instead of dropping them all
        # to keep the initialisation done at instantiation of opa_storage
        c.delete_many({})

    yield


@pytest.fixture(params=StockValueType)
def stock_value_type(request):
    return request.param


@pytest.fixture
def stock_values_serie(stock_value_type, ticker) -> list[StockValue]:
    start = fake.date_time()

    if stock_value_type == StockValueType.HISTORICAL:
        dates = [start + timedelta(days=n) for n in range(100)]
    elif stock_value_type == StockValueType.STREAMING:
        dates = [start + timedelta(minutes=15 * n) for n in range(100)]

    return [StockValue(ticker=ticker, date=d, close=fake_value()) for d in dates]


@pytest.mark.usefixtures("db_wipeout")
class TestIntegration:
    def test_values_retrieval(self, ticker, stock_values_serie, stock_value_type):
        """`get_values` should return all the values that were inserted via `insert_values`,
        sorted by most-recent first"""
        opa_storage.insert_values(stock_values_serie, stock_value_type)

        expected = sorted(stock_values_serie, key=lambda v: v.date, reverse=True)

        assert opa_storage.get_values(ticker, stock_value_type) == expected

    def test_company_info_retrieval(self, company_infos):
        opa_storage.insert_company_infos(company_infos)

        expected = {c.symbol: c for c in company_infos}
        symbols = [c.symbol for c in company_infos]

        assert opa_storage.get_company_infos(symbols) == expected

    def test_all_tickers(self, company_infos):
        """`get_all_tickers` should return all the tickers for which we have company info,
        in no particular order"""
        opa_storage.insert_company_infos(company_infos)

        expected = sorted([c.symbol for c in company_infos])

        all_tickers = opa_storage.get_all_tickers()
        assert sorted(all_tickers) == expected

    def test_stats(self, ticker, stock_values_serie, stock_value_type):
        """`get_stats` should return coherent stats on the input ticker"""
        opa_storage.insert_values(stock_values_serie, stock_value_type)

        expected = {
            ticker: StockCollectionStats(
                oldest=min((v.date for v in stock_values_serie)),
                latest=max((v.date for v in stock_values_serie)),
                count=len(stock_values_serie),
            )
        }

        assert opa_storage.get_stats(stock_value_type) == expected