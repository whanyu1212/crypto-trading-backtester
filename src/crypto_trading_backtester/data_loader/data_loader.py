from .loaders.base_loader import CryptoDataLoader
from .loaders.fmp_loader import FinancialModelingPrepLoader


class LoaderFactory:
    _loaders = {
        "fmp": FinancialModelingPrepLoader,
    }

    @staticmethod
    def create_loader(loader_type: str) -> CryptoDataLoader:
        loader_class = LoaderFactory._loaders.get(loader_type)
        if not loader_class:
            raise ValueError(f"Unknown loader type: {loader_type}")
        return loader_class()


def load_crypto_data(loader_type: str, crypto_symbol: str = None):
    loader = LoaderFactory.create_loader(loader_type)
    return loader.fetch_crypto_pricing(crypto_symbol)
