from abc import ABC, abstractmethod
import pandas as pd


# Strategy Interface
class TradingStrategy(ABC):
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass
