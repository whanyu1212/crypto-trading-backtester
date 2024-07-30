import pandas as pd
import numpy as np
from .strategy_interface import TradingStrategy


class SMAStrategy(TradingStrategy):
    def __init__(self, short_window: int, long_window: int):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy and sell signals based on SMA crossovers.

        Args:
        data (pd.DataFrame): DataFrame containing 'close' prices.

        Returns:
        pd.DataFrame: DataFrame with signals (1 for buy, -1 for sell, 0 for hold).
        """
        # Initialize the DataFrame for strategy signals
        signals = pd.DataFrame(index=data.index)
        signals["signal"] = 0.0

        # Create the short and long simple moving averages
        signals["short_mavg"] = (
            data["close"]
            .rolling(window=self.short_window, min_periods=1, center=False)
            .mean()
        )
        signals["long_mavg"] = (
            data["close"]
            .rolling(window=self.long_window, min_periods=1, center=False)
            .mean()
        )

        # Create signals
        signals["signal"][self.short_window :] = np.where(
            signals["short_mavg"][self.short_window :]
            > signals["long_mavg"][self.short_window :],
            1.0,
            0.0,
        )

        # Generate trading orders
        signals["positions"] = signals["signal"].diff()

        # Mapping the positions to our defined buy/sell/hold signals:
        # Buy (1) when position changes from 0 to 1
        # Sell (-1) when position changes from 1 to 0
        signals["signals"] = signals["positions"].apply(
            lambda x: 1 if x > 0 else -1 if x < 0 else 0
        )

        return signals[["signals"]]


# Example usage:
# data = pd.DataFrame({'close': [random price data]})
# sma_strategy = SMAStrategy(short_window=40, long_window=100)
# signals = sma_strategy.generate_signals(data)
# print(signals.head())
