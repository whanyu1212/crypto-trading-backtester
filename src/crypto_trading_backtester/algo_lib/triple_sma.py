import math
import pandas as pd
from typing import Union
from colorama import init, Fore

init(autoreset=True)


class TripleSMAVectorBacktester:
    def __init__(
        self,
        df: pd.DataFrame,
        initial_capital: Union[int, float] = 100000,
        in_position: bool = False,
        SMA1: int = 10,
        SMA2: int = 20,
        SMA3: int = 50,
        starting_share: int = 0,
    ):

        # Run time error checks
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("df must be a non-empty DataFrame")
        if not "close" in df.columns:
            raise ValueError("No close column found")
        if not isinstance(initial_capital, (int, float)) or initial_capital <= 0:
            raise ValueError("initial_capital must be a positive number")
        if not isinstance(in_position, bool):
            raise ValueError("in_position must be a boolean")
        if not isinstance(SMA1, int) or SMA1 <= 0:
            raise ValueError("SMA1 must be a positive integer")
        if not isinstance(SMA2, int) or SMA2 <= 0:
            raise ValueError("SMA2 must be a positive integer")
        if not isinstance(SMA3, int) or SMA3 <= 0:
            raise ValueError("SMA3 must be a positive integer")
        if not SMA1 < SMA2 < SMA3:
            raise ValueError("SMA1, SMA2, and SMA3 must be in ascending order")

        self.df = df.sort_values("date").reset_index(drop=True)
        self.initial_capital = initial_capital
        self.SMA1 = SMA1
        self.SMA2 = SMA2
        self.SMA3 = SMA3
        self.in_position = in_position
        self.balance = self.initial_capital
        self.no_of_shares = starting_share

    def calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages for different window sizes (short, medium, long)

        Args:
            df (pd.DataFrame): input dataframe

        Returns:
            pd.DataFrame: output dataframe with new columns added
        """
        df["SMA1"] = df["close"].rolling(window=self.SMA1).mean()
        df["SMA2"] = df["close"].rolling(window=self.SMA2).mean()
        df["SMA3"] = df["close"].rolling(window=self.SMA3).mean()

        return df

    def calculate_daily_market_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily market return

        Args:
            df (pd.DataFrame): input dataframe

        Returns:
            pd.DataFrame: output dataframe with new columns added
        """
        df["market_return"] = df["close"].pct_change()

        return df

    def set_up_trading_state(self, df: pd.DataFrame) -> pd.DataFrame:
        """Setting up the initial trading state

        Args:
            df (pd.DataFrame): input dataframe

        Returns:
            pd.DataFrame: output dataframe with new columns added
            and initial values set (index 0)
        """
        initial_values = {
            "in_position": (self.in_position, "bool"),
            "balance": (self.balance, "float64"),
            "no_shares": (self.no_of_shares, "float64"),
        }

        for column, (initial_value, dtype) in initial_values.items():
            df[column] = pd.Series(dtype=dtype)
            df.loc[0, column] = initial_value

        return df

    def buy_signal(self, df: pd.DataFrame, i: int) -> bool:
        """Check if the current index is a buy signal

        Args:
            df (pd.DataFrame): input dataframe
            i (int): index

        Returns:
            bool: True or False
        """
        if (
            df["SMA2"][i - 1] < df["SMA3"][i - 1]
            and df["SMA2"][i] > df["SMA3"][i]
            and df["SMA1"][i] > df["SMA2"][i]
            and df["close"][i] > df["SMA1"][i]
            and self.in_position == False
        ):
            return True

    def sell_signal(self, df: pd.DataFrame, i: int) -> bool:
        """Check if the current index is a sell signal

        Args:
            df (pd.DataFrame): input dataframe
            i (int): index

        Returns:
            bool: True or False
        """
        if (
            df["SMA2"][i - 1] > df["SMA3"][i - 1]
            and df["SMA2"][i] < df["SMA3"][i]
            and df["SMA1"][i] < df["SMA2"][i]
            and df["close"][i] < df["SMA1"][i]
            and self.in_position == True
        ):
            return True

    def backtest_strategy(self, df):
        for i in range(1, len(df)):
            if self.buy_signal(df, i):
                print(Fore.GREEN + "Buy Signal")  # Green text for buy signal
                print()
                self.no_of_shares = math.floor(self.balance / df.loc[i, "close"])
                self.balance -= self.no_of_shares * df.loc[i, "close"]
                self.in_position = True
                print(
                    Fore.GREEN
                    + f"Buying {self.no_of_shares} shares at {df.loc[i, 'close']}, balance: {self.balance}"
                )
                print()
            elif self.sell_signal(df, i):
                print(Fore.RED + "Sell Signal")  # Red text for sell signal
                print()
                print(
                    Fore.RED
                    + f"Selling {self.no_of_shares} shares at {df.loc[i-1, 'close']}, balance: {self.balance}"
                )
                print()
                self.balance += self.no_of_shares * df.loc[i, "close"]
                self.no_of_shares = 0
                self.in_position = False
                

            df.loc[i, "no_shares"] = self.no_of_shares
            df.loc[i, "balance"] = self.balance
            df.loc[i, "in_position"] = self.in_position

        if self.in_position:
            self.balance += self.no_of_shares * df.loc[df.index[-1], "close"]
            self.no_of_shares = 0
            self.in_position = False
            df.loc[df.index[-1], "no_shares"] = self.no_of_shares
            df.loc[df.index[-1], "balance"] = self.balance
            df.loc[df.index[-1], "in_position"] = self.in_position

        print(Fore.WHITE + f"Final balance: {self.balance}")
        print()

        return df

    def backtesting_flow(self):
        df = self.df.copy()
        df = self.calculate_moving_averages(df)
        df = self.calculate_daily_market_return(df)
        df = self.set_up_trading_state(df)
        df = self.backtest_strategy(df)

        # return df
