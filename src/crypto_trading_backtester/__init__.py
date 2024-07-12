# read version from installed package
# from importlib.metadata import version
# __version__ = version("crypto_trading_backtester")
from .data_loader.fetch_crypto_pricing_data import FetchCryptoPricingData

get_pricing_data = FetchCryptoPricingData.get_pricing_data
