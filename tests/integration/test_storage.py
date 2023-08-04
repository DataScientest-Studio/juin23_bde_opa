from opa.storage import opa_storage


class TestGetAllTickers:
    def test_pouet(self):
        all_tickers = opa_storage.get_all_tickers()
        assert isinstance(all_tickers, list)
        assert all_tickers != []
