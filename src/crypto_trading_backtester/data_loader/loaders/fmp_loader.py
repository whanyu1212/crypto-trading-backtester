import os
import requests
import pandas as pd
from dotenv import load_dotenv
from typing import List
from requests.exceptions import RequestException
from loguru import logger
from .base_loader import CryptoDataLoader

load_dotenv()


class FinancialModelingPrepLoader(CryptoDataLoader):
    def __init__(self):
        self.api_key = os.getenv("DATA_API_KEY")
        self.base_url_crypto_list = os.getenv("BASE_URL_CRYPTO_LIST")
        self.base_url_crypto_price = os.getenv("BASE_URL_CRYPTO_PRICE")
        self._valid_crypto_list = None

    def fetch_all_cryptos(self) -> List[str]:
        """Fetch a complete list of cryptocurrencies available on financialmodellingprep.com.

        Raises:
            ValueError: If the request fails with a non-200 status code.
            SystemError: If a request exception occurs.

        Returns:
            List[str]: A list of valid cryptocurrency symbols.
        """
        if self._valid_crypto_list is None:
            try:
                url = f"{self.base_url_crypto_list}apikey={self.api_key}"
                response = requests.get(url)

                if response.status_code == 200:
                    logger.success(
                        "Request for fetching cryptocurrency list was successful"
                    )
                    data = response.json()
                    self._valid_crypto_list = [
                        d["symbol"] for d in data if "symbol" in d
                    ]
                else:
                    raise ValueError(
                        f"Failed to fetch cryptocurrencies, status code: {response.status_code}"
                    )
            except RequestException as e:
                raise SystemError(
                    f"An error occurred while fetching cryptocurrencies: {e}"
                )
        return self._valid_crypto_list

    def is_valid_crypto(self, crypto_symbol: str) -> bool:
        """Check if the given cryptocurrency symbol is valid.

        Args:
            crypto_symbol (str): The cryptocurrency symbol to validate.

        Returns:
            bool: True if the symbol is valid, False otherwise.
        """
        valid_crypto_list = self.fetch_all_cryptos()
        return crypto_symbol in valid_crypto_list

    def fetch_crypto_pricing(self, crypto_symbol: str) -> pd.DataFrame:
        """Fetch the pricing data for a given cryptocurrency symbol.

        Args:
            crypto_symbol (str): The cryptocurrency symbol to fetch pricing data for.

        Raises:
            ValueError: If the cryptocurrency symbol is not valid or if the request fails with a non-200 status code.
            SystemError: If a request exception occurs.

        Returns:
            pd.DataFrame: A DataFrame containing the historical pricing data.
        """
        if not self.is_valid_crypto(crypto_symbol):
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
                    f"Failed to fetch cryptocurrency pricing data, status code: {response.status_code}"
                )
        except RequestException as e:
            raise SystemError(
                f"An error occurred while fetching cryptocurrency pricing data: {e}"
            )
