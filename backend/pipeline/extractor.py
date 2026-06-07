import yfinance as yf
import pandas as pd
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class Extractor:
    def __init__(self, tickers: List[str]):
        self.tickers = tickers

    def fetch_historical_data(self, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetches historical OHLCV data for all tickers.
        """
        try:
            logger.info(f"Fetching {period} historical data for {len(self.tickers)} tickers...")
            # group_by='ticker' returns a MultiIndex column DataFrame if multiple tickers are passed
            data = yf.download(self.tickers, period=period, interval=interval, group_by='ticker', threads=True)
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None

    def fetch_latest_data(self) -> Optional[pd.DataFrame]:
        """
        Fetches the latest intraday data (useful for updates).
        """
        # Fetch last 5 days with 15-minute intervals to ensure we have the latest and some buffer
        return self.fetch_historical_data(period="5d", interval="15m")
