import pandas as pd
from .strategies.sma import SMAStrategy
from .strategies.strategy_interface import TradingStrategy

# Strategy Registry
STRATEGIES = {"sma": SMAStrategy}


def create_strategy(strategy_name, *args, **kwargs):
    """
    Factory function to instantiate strategies based on name and parameters.
    """
    strategy_class = STRATEGIES.get(strategy_name)
    if strategy_class is None:
        raise ValueError(f"Strategy {strategy_name} is not supported.")
    return strategy_class(*args, **kwargs)


class CryptoTradingBacktester:
    def __init__(self, strategy):
        self.strategy = strategy

    def backtest(self, data: pd.DataFrame):
        return self.strategy.generate_signals(data)


def run_backtest(strategy_name, data, *args, **kwargs):
    """
    Run a backtest with the specified strategy and parameters.
    """
    strategy = create_strategy(strategy_name, *args, **kwargs)
    backtester = CryptoTradingBacktester(strategy)
    return backtester.backtest(data)
