import logging
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from models.schemas import Price, Metric, Stock
from datetime import datetime

logger = logging.getLogger(__name__)

class Loader:
    def __init__(self, db_session: Session):
        self.db = db_session

    def load_prices(self, prices_df: pd.DataFrame) -> int:
        if prices_df is None or prices_df.empty:
            return 0
        
        records = prices_df.to_dict('records')
        chunk_size = 100
        rows_processed = 0

        try:
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i + chunk_size]
                dialect_name = self.db.get_bind().dialect.name
                if dialect_name == 'postgresql':
                    stmt = pg_insert(Price).values(chunk)
                else:
                    stmt = sqlite_insert(Price).values(chunk)

                on_duplicate_key_stmt = stmt.on_conflict_do_update(
                    index_elements=['ticker', 'date'],
                    set_=dict(
                        open=stmt.excluded.open,
                        high=stmt.excluded.high,
                        low=stmt.excluded.low,
                        close=stmt.excluded.close,
                        volume=stmt.excluded.volume
                    )
                )
                self.db.execute(on_duplicate_key_stmt)
            self.db.commit()
            rows_processed = len(records)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error loading prices: {e}")
            raise e
        
        return rows_processed

    def load_metrics(self, metrics_df: pd.DataFrame) -> int:
        if metrics_df is None or metrics_df.empty:
            return 0
        
        records = metrics_df.to_dict('records')
        chunk_size = 100
        rows_processed = 0

        try:
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i + chunk_size]
                dialect_name = self.db.get_bind().dialect.name
                if dialect_name == 'postgresql':
                    stmt = pg_insert(Metric).values(chunk)
                else:
                    stmt = sqlite_insert(Metric).values(chunk)

                on_duplicate_key_stmt = stmt.on_conflict_do_update(
                    index_elements=['ticker', 'date'],
                    set_=dict(
                        sma_7=stmt.excluded.sma_7,
                        sma_30=stmt.excluded.sma_30,
                        rsi=stmt.excluded.rsi,
                        volatility=stmt.excluded.volatility,
                        vwap=stmt.excluded.vwap
                    )
                )
                self.db.execute(on_duplicate_key_stmt)
            self.db.commit()
            rows_processed = len(records)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error loading metrics: {e}")
            raise e
        
        return rows_processed
