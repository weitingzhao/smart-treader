import logging
import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from src.services.loading.loader.abstract_loader import AbstractLoader


logger = logging.getLogger(__name__)


class TradingCsvLoader(AbstractLoader):
    """
    A class to load Daily or higher timeframe data from CSV files.

    Parameters:
    :param config: User config
    :type config: dict
    :param timeframe: daily, weekly or monthly
    :type timeframe: str
    :param end_date: End date up to which date must be returned
    :type end_date: Optional[datetime]
    :param period: Number of lines to return from end_date or end of file

    """

    timeframes = dict(daily="D", weekly="W-SUN", monthly="MS")

    def __init__(
            self,
            config: dict,
            tf: Optional[str] = None,
            end_date: Optional[datetime] = None,
            period: int = 160,
    ):
        # Closed: No need to close method to be called for this Class
        self.closed = True
        # Time frame
        self.default_timeframe = str(config.get("DEFAULT_TF", "daily"))
        if self.default_timeframe not in self.timeframes:
            valid_values = ", ".join(self.timeframes.keys())
            raise ValueError(f"`DEFAULT_TF` in config must be one of {valid_values}")
        if tf is None:
            tf = self.default_timeframe
        if tf not in self.timeframes:
            valid_values = ", ".join(self.timeframes.keys())
            raise ValueError(f"Timeframe must be one of {valid_values}")
        self.timeframe = tf
        # offset_str
        self.offset_str = self.timeframes[tf]
        # end_date
        self.end_date = end_date
        if end_date:
            if self.timeframe == "weekly":
                self.end_date = self.last_day_week(end_date)
            elif self.timeframe == "monthly":
                self.end_date = self.last_day_month(end_date)

        self.data_path = Path(config["DATA_PATH"]).expanduser()
        self.ohlc_dict = dict(
            Open="first",
            High="max",
            Low="min",
            Close="last",
            Volume="sum",
        )

        self.chunk_size = 1024 * 6

        if tf == self.default_timeframe:
            self.period = period
        elif tf == "weekly":
            self.period = 7 * period
            self.chunk_size = 1024 * 19
        elif tf == "monthly":
            days = 7 if self.default_timeframe == "weekly" else 1
            self.period = 30 * period // days

    def get(self, symbol: str) -> Optional[pd.DataFrame]:

        file = self.data_path / f"{symbol.upper()}.csv"
        if not file.exists():
            logger.warning(f"File not found: {file}")
            return

        if self.timeframe == "monthly":
            # It is faster to load the entire file for monthly
            # Considering the average size of file
            return self.process_monthly(file, self.end_date)

        try:
            csv_loader = loader.CsvLoader(file)
            df = csv_loader.load_symbol_history(
                period=self.period,
                end_date=self.end_date,
                chunk_size=self.chunk_size
            )
        except (IndexError, ValueError):
            return

        if self.timeframe == self.default_timeframe or df.empty:
            return df

        df = df.resample(self.offset_str).agg(self.ohlc_dict).dropna()
        assert isinstance(df, pd.DataFrame)
        return df

    def process_monthly(self, file, end_date) -> pd.DataFrame:
        df = pd.read_csv(
            file,
            index_col="Date",
            parse_dates=["Date"],
        )
        if end_date:
            df = df.loc[:end_date].iloc[-self.period:]
        else:
            df = df.iloc[-self.period:]
        df = df.resample(self.offset_str).agg(self.ohlc_dict).dropna()
        assert isinstance(df, pd.DataFrame)
        return df

    @staticmethod
    def last_day_week(date: datetime) -> datetime:
        """Given a date returns the date for Saturday"""
        weekday = date.weekday()
        if weekday == 5:
            # saturday
            return date
        remaining_days = 5 - weekday
        if remaining_days == -1:
            # It's sunday
            remaining_days += 7
        return date + timedelta(remaining_days)

    @staticmethod
    def last_day_month(date: datetime) -> datetime:
        """Given a date returns the date for last day of month"""
        month = date.month % 12 + 1
        year = date.year + (1 if month == 1 else 0)
        return datetime(year, month, 1) - timedelta(1)

    def close(self):
        """Not required here as nothing to close"""
        pass
