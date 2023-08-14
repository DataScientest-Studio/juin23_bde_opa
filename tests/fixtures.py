from datetime import timedelta

import pytest
from faker import Faker

from opa.core import CompanyInfo, StockValue, StockValueType

fake = Faker()


def fake_ticker() -> str:
    return fake.pystr(max_chars=5).upper()


def fake_value() -> float:
    return fake.pyfloat(right_digits=2, min_value=0.5, max_value=100.0)


@pytest.fixture(params=StockValueType)
def stock_value_type(request):
    return request.param


@pytest.fixture
def ticker():
    return fake_ticker()


@pytest.fixture
def stock_values_serie(stock_value_type, ticker) -> list[StockValue]:
    start = fake.date_time()

    if stock_value_type == StockValueType.HISTORICAL:
        dates = [start + timedelta(days=n) for n in range(100)]
        interval = 15 * 60  # 15 minutes
    elif stock_value_type == StockValueType.STREAMING:
        dates = [start + timedelta(minutes=15 * n) for n in range(100)]
        interval = 24 * 60 * 60  # one day

    return [
        StockValue(ticker=ticker, date=d, interval=interval, close=fake_value())
        for d in dates
    ]


@pytest.fixture
def company_infos() -> list[CompanyInfo]:
    return [
        CompanyInfo(
            symbol=fake_ticker(),
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
