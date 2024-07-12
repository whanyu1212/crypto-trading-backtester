import os
import requests
import pandas as pd
from dotenv import load_dotenv
from typing import List
from requests.exceptions import RequestException
from loguru import logger

load_dotenv()


class FetchCryptoPricingData:
    def __init__(self):
        self.api_key = os.getenv("DATA_API_KEY")
        self.base_url_crypto_list = os.getenv("BASE_URL_CRYPTO_LIST")
        self.base_url_crypto_price = os.getenv("BASE_URL_CRYPTO_PRICE")

    def fetch_all_cryptos(self) -> List[str]:
        """Fetch a complete list of cryptocurrencies
        that are available on financialmodellingprep.com
        to compare against the user input. If the user
        input is not in the list, then raise an error.

        Raises:
            ValueError: _description_
            SystemError: _description_

        Returns:
            List[str]: _description_
        """
        try:
            url = f"{self.base_url_crypto_list}apikey={self.api_key}"
            response = requests.get(url)

            if response.status_code == 200:
                logger.success(
                    "Request for fetching cryptocurrency list was successful"
                )
                data = response.json()
                valid_crypto_list = [d["symbol"] for d in data if "symbol" in d]
                return valid_crypto_list
            else:
                raise ValueError(
                    f"Failed to fetch cryptocurrencies, status code: "
                    f"{response.status_code}"
                )
        except RequestException as e:
            raise SystemError(
                "An error occurred while fetching cryptocurrencies: " f"{e}"
            )

    def fetch_crypto_pricing(self, crypto_symbol: str) -> pd.DataFrame:
        """Fetch historical pricing data for a given cryptocurrency symbol.

        Args:
            crypto_symbol (str): The symbol of the cryptocurrency for which
            to fetch pricing data. e.g, BTCUSD, ETHUSD, etc.

        Raises:
            ValueError: not a valid cryptocurrency symbol.
            ValueError: failed to fetch cryptocurrency pricing data.
            SystemError: request error occurred while fetching cryptocurrency pricing data.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the historical pricing data.
        """
        valid_crypto_list = self.fetch_all_cryptos()
        if crypto_symbol not in valid_crypto_list:
            raise ValueError(f"{crypto_symbol} is not a valid cryptocurrency symbol.")
        try:
            url = f"{self.base_url_crypto_price}{crypto_symbol}?apikey={self.api_key}"
            response = requests.get(url)

            if response.status_code == 200:
                logger.success(
                    f"Request for {crypto_symbol} pricing data was successful"
                )
                data = response.json()
                return (
                    pd.DataFrame(data["historical"])
                    .sort_values("date")
                    .reset_index(drop=True)
                )
            else:
                raise ValueError(
                    "Failed to fetch cryptocurrency pricing data for "
                    f"{crypto_symbol}, status code: {response.status_code}"
                )
        except RequestException as e:
            raise SystemError(
                "An error occurred while fetching cryptocurrency pricing data "
                f"for {crypto_symbol}: {e}"
            )

    @classmethod
    def get_pricing_data(cls, symbol: str):
        instance = (
            cls()
        )  # Assuming the class does not require a symbol for initialization
        return instance.fetch_crypto_pricing(symbol)


# sample usage

if __name__ == "__main__":
    fcpd = FetchCryptoPricingData()
    data = fcpd.fetch_crypto_pricing("BTCUSD")
    print(data.head())
