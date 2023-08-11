import pytest
import os
from faker import Faker

from opa.core import CompanyInfo
from opa.storage import opa_storage


fake = Faker()


@pytest.fixture(scope="function")
def db_wipeout():
    # This relies on knowledge of opa_storage implementation but it's good enough
    # in this scope
    for c in opa_storage.collections.values():
        # We delete all the data in each collection instead of dropping them all
        # to keep the initialisation done at instantiation of opa_storage
        c.delete_many({})

    yield


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
    def test_company_info_retrieval(self, company_infos, db_wipeout):
        opa_storage.insert_company_infos(company_infos)

        expected = {c.symbol: c for c in company_infos}
        symbols = [c.symbol for c in company_infos]

        assert opa_storage.get_company_infos(symbols) == expected
