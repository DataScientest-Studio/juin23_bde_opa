import pytest
from faker import Faker
from datetime import timedelta

from opa.core import CompanyInfo, StockValue, StockValueType
from opa.storage import opa_storage


fake = Faker()


@pytest.fixture(scope="function", autouse=True)
def db_wipeout():
    # This relies on knowledge of opa_storage implementation but it's good enough
    # in this scope
    for c in opa_storage.collections.values():
        # We delete all the data in each collection instead of dropping them all
        # to keep the initialisation done at instantiation of opa_storage
        c.delete_many({})

    yield


@pytest.fixture
def ticker():
    return fake.pystr(max_chars=5).upper()


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

    return [
        StockValue(
            ticker=ticker,
            date=d,
            close=fake.pyfloat(right_digits=2, min_value=0.5, max_value=100.0),
        )
        for d in dates
    ]


@pytest.fixture
def company_infos() -> list[CompanyInfo]:
    return [
        CompanyInfo(
            symbol=fake.pystr(max_chars=5).upper(),
            name=fake.company(),
            website=fake.url(),
            description=fake.text(),
            currency=fake.currency_symbol(),
            sector=fake.word(),
            country=fake.country(),
            image=fake.url(),
            ipo_date=fake.date_time(),
            address=fake.address(),
            city=fake.city(),
        )
        for _ in range(10)
    ]


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
