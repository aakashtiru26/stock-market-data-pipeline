import pandas as pd
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class Transformer:
    @staticmethod
    def clean_and_transform(raw_data: pd.DataFrame, is_multi_ticker: bool = True) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Takes raw yfinance DataFrame and returns structured (prices_df, metrics_df)
        """
        if raw_data is None or raw_data.empty:
            logger.warning("Empty data provided for transformation.")
            return None, None

        try:
            prices_list = []
            metrics_list = []

            # yfinance returns MultiIndex columns (Ticker, Price_Type) when multiple tickers are passed
            if is_multi_ticker and isinstance(raw_data.columns, pd.MultiIndex):
                tickers = raw_data.columns.levels[0]
            else:
                tickers = ['UNKNOWN'] # Fallback if single ticker passed without MultiIndex

            for ticker in tickers:
                if is_multi_ticker and isinstance(raw_data.columns, pd.MultiIndex):
                    df = raw_data[ticker].copy()
                else:
                    df = raw_data.copy()
                    ticker = df.name if hasattr(df, 'name') else 'UNKNOWN'

                df = df.dropna(subset=['Close']) # Drop rows without closing prices
                
                # Basic Prices
                price_df = pd.DataFrame()
                price_df['ticker'] = [ticker] * len(df)
                price_df['date'] = df.index
                price_df['open'] = df['Open'].values
                price_df['high'] = df['High'].values
                price_df['low'] = df['Low'].values
                price_df['close'] = df['Close'].values
                price_df['volume'] = df['Volume'].values
                
                prices_list.append(price_df)

                # Metrics Calculation
                metric_df = pd.DataFrame()
                metric_df['ticker'] = [ticker] * len(df)
                metric_df['date'] = df.index
                
                # SMA
                metric_df['sma_7'] = df['Close'].rolling(window=7, min_periods=1).mean().values
                metric_df['sma_30'] = df['Close'].rolling(window=30, min_periods=1).mean().values
                
                # Daily Return and Volatility (rolling std dev of returns)
                daily_return = df['Close'].pct_change()
                metric_df['volatility'] = (daily_return.rolling(window=30, min_periods=1).std() * np.sqrt(252)).values

                # RSI (14 period)
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
                rs = gain / loss
                metric_df['rsi'] = (100 - (100 / (1 + rs))).values

                # VWAP (Cumulative)
                typical_price = (df['High'] + df['Low'] + df['Close']) / 3
                # For intraday, VWAP is usually daily. For historical, we can do a rolling or cumulative.
                # Let's do a simple rolling VWAP for demonstration over 14 periods.
                rolling_volume = df['Volume'].rolling(window=14, min_periods=1).sum()
                rolling_tp_vol = (typical_price * df['Volume']).rolling(window=14, min_periods=1).sum()
                metric_df['vwap'] = (rolling_tp_vol / rolling_volume).values

                # Drop NaNs created by rolling windows where appropriate, or replace with None/NaN for DB
                metric_df = metric_df.replace({np.nan: None})

                metrics_list.append(metric_df)

            final_prices = pd.concat(prices_list, ignore_index=True)
            final_metrics = pd.concat(metrics_list, ignore_index=True)
            
            # Final cleaning
            final_prices = final_prices.replace({np.nan: None})
            
            return final_prices, final_metrics
            
        except Exception as e:
            logger.error(f"Error in transformation: {e}")
            return None, None
