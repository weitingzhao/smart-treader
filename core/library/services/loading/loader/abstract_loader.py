import pandas as pd
from typing import Optional
from datetime import datetime
from abc import ABC, abstractmethod


class AbstractLoader(ABC):
    """Abstract base class to be implemented by all Loader classes
    :param config: User config
    :type config: dict
    :param timeframe: Any timeframe string accepted by the class
    :type timeframe: str
    :param end_date: End date upto which date must be returned
    :type end_date: Optional[datetime]
    :param period: Number of lines to return from end_date or end of file
    """

    # A dict of key-value pairs.
    # Key must be valid timeframe strings passed to --tf option
    # Value must be string used internally for resampling or other purposes
    timeframes: dict
    # The currently active timeframe.
    timeframe: str
    # Current status of Loader. Close method will not be called, if value is True
    closed: bool

    @abstractmethod
    def __init__(self, config: dict, tf: str, end_date: Optional[datetime] = None, period: int = 160):
        pass

    @abstractmethod
    def get(self, symbol: str) -> Optional[pd.DataFrame]:
        """Returns OHLC data for symbol as a pandas DataFrame
        :param symbol: Instrument symbol
        :type symbol: str
        """
        pass

    @abstractmethod
    def close(self):
        """Close pending database connections, network sessions or other cleanup operations"""
        pass
