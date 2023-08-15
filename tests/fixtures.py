from datetime import timedelta

import pytest
from faker import Faker

from opa.core import CompanyInfo, StockValue, StockValueKind, StockValueSerieGranularity

fake = Faker()


def fake_ticker() -> str:
    return fake.pystr(max_chars=5).upper()


def fake_value() -> float:
    return fake.pyfloat(right_digits=2, min_value=0.5, max_value=100.0)


def fake_volume() -> int:
    return fake.pyint(min_value=1000)


@pytest.fixture(params=StockValueKind)
def stock_value_kind(request):
    return request.param


@pytest.fixture(params=StockValueSerieGranularity)
def stock_value_serie_granularity(request):
    return request.param


@pytest.fixture
def ticker():
    return fake_ticker()


@pytest.fixture
def stock_values_serie(
    stock_value_kind, stock_value_serie_granularity, ticker
) -> list[StockValue]:
    start = fake.date_time()

    if stock_value_kind == StockValueKind.OHLC:
        kwargs_fn = lambda: {
            "open": fake_value(),
            "low": fake_value(),
            "high": fake_value(),
            "volume": fake_volume(),
        }
    elif stock_value_kind == StockValueKind.SIMPLE:
        kwargs_fn = lambda: {}

    if stock_value_serie_granularity == StockValueSerieGranularity.COARSE:
        dates = [start + timedelta(minutes=15 * n) for n in range(100)]
        interval = 24 * 60 * 60  # one day
    elif stock_value_serie_granularity == StockValueSerieGranularity.FINE:
        dates = [start + timedelta(days=n) for n in range(100)]
        interval = 15 * 60  # 15 minutes

    return [
        StockValue(
            ticker=ticker, date=d, interval=interval, close=fake_value(), **kwargs_fn()
        )
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
