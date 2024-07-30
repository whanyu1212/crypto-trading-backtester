from abc import ABC, abstractmethod
from typing import List
import pandas as pd


class CryptoDataLoader(ABC):
    @abstractmethod
    def fetch_all_cryptos(self) -> List[str]:
        pass

    @abstractmethod
    def fetch_crypto_pricing(self, crypto_symbol: str) -> pd.DataFrame:
        pass
