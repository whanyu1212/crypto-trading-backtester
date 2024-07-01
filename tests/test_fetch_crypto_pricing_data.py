import pytest
import requests
import requests_mock
import os
import pandas as pd
from crypto_trading_backtester.data_loader.fetch_crypto_pricing_data import (
    FetchCryptoPricingData,
)


@pytest.fixture(scope="module", autouse=True)
def set_env_vars():

    # set up the environment variables for the tests
    os.environ["DATA_API_KEY"] = "test_api_key"
    os.environ["BASE_URL_CRYPTO_LIST"] = "http://mock-api.com/crypto-list?"
    os.environ["BASE_URL_CRYPTO_PRICE"] = "http://mock-api.com/crypto-price/"

    # separte the setup and teardown code from the tests
    yield

    # tear down all the environment variables after the tests have been run
    del os.environ["DATA_API_KEY"]
    del os.environ["BASE_URL_CRYPTO_LIST"]
    del os.environ["BASE_URL_CRYPTO_PRICE"]


@pytest.fixture
def fetcher():
    return FetchCryptoPricingData()


def test_fetch_all_cryptos_success(fetcher):
    # mock https requests
    with requests_mock.Mocker() as m:
        mock_response = [
            {"symbol": "BTCUSD"},
            {"symbol": "ETHUSD"},
            {"symbol": "XRPUSD"},
        ]
        # mock the GET request to the designated url
        m.get(fetcher.base_url_crypto_list + "apikey=test_api_key", json=mock_response)

        result = fetcher.fetch_all_cryptos()
        assert result == ["BTCUSD", "ETHUSD", "XRPUSD"]


# Test fetch_all_cryptos failure
def test_fetch_all_cryptos_failure(fetcher):
    with requests_mock.Mocker() as m:
        m.get(fetcher.base_url_crypto_list + "apikey=test_api_key", status_code=404)

        with pytest.raises(ValueError, match="Failed to fetch cryptocurrencies"):
            fetcher.fetch_all_cryptos()


# Test fetch_crypto_pricing success
def test_fetch_crypto_pricing_success(fetcher):
    with requests_mock.Mocker() as m:
        mock_crypto_list = [
            {"symbol": "BTCUSD"},
            {"symbol": "ETHUSD"},
            {"symbol": "XRPUSD"},
        ]
        mock_pricing_data = {
            "symbol": "BTCUSD",
            "historical": [
                {
                    "date": "2023-01-01",
                    "open": 30000,
                    "high": 32000,
                    "low": 29000,
                    "close": 31000,
                },
                {
                    "date": "2023-01-02",
                    "open": 31000,
                    "high": 33000,
                    "low": 30000,
                    "close": 32000,
                },
            ],
        }
        m.get(
            fetcher.base_url_crypto_list + "apikey=test_api_key", json=mock_crypto_list
        )
        m.get(
            fetcher.base_url_crypto_price + "BTCUSD?apikey=test_api_key",
            json=mock_pricing_data,
        )

        result = fetcher.fetch_crypto_pricing("BTCUSD")
        expected_result = pd.DataFrame(mock_pricing_data["historical"])
        pd.testing.assert_frame_equal(result, expected_result)


# Test fetch_crypto_pricing invalid symbol
def test_fetch_crypto_pricing_invalid_symbol(fetcher):
    with requests_mock.Mocker() as m:
        mock_crypto_list = [
            {"symbol": "BTCUSD"},
            {"symbol": "ETHUSD"},
            {"symbol": "XRPUSD"},
        ]
        m.get(
            fetcher.base_url_crypto_list + "apikey=test_api_key", json=mock_crypto_list
        )

        with pytest.raises(ValueError, match="is not a valid cryptocurrency symbol"):
            fetcher.fetch_crypto_pricing("INVALID")


# Test fetch_crypto_pricing failure
def test_fetch_crypto_pricing_failure(fetcher):
    with requests_mock.Mocker() as m:
        mock_crypto_list = [
            {"symbol": "BTCUSD"},
            {"symbol": "ETHUSD"},
            {"symbol": "XRPUSD"},
        ]
        m.get(
            fetcher.base_url_crypto_list + "apikey=test_api_key", json=mock_crypto_list
        )
        m.get(
            fetcher.base_url_crypto_price + "BTCUSD?apikey=test_api_key",
            status_code=404,
        )

        with pytest.raises(
            ValueError, match="Failed to fetch cryptocurrency pricing data"
        ):
            fetcher.fetch_crypto_pricing("BTCUSD")
