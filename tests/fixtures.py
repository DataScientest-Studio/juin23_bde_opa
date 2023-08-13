from datetime import timedelta

import pytest
from faker import Faker

from opa.core import CompanyInfo, StockValue, StockValueType, StockCollectionStats

fake = Faker()


def fake_ticker() -> str:
    return fake.pystr(max_chars=5).upper()


@pytest.fixture
def ticker():
    return fake_ticker()


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
