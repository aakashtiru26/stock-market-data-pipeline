import logging
import uuid
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.schemas import PipelineLog
from pipeline.extractor import Extractor
from pipeline.transformer import Transformer
from pipeline.loader import Loader

logger = logging.getLogger(__name__)

TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'JPM', 'V', 'JNJ']

def run_pipeline(is_historical: bool = False):
    run_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    status = "RUNNING"
    error_message = None
    rows_processed = 0

    logger.info(f"Starting pipeline run: {run_id} (Historical: {is_historical})")

    db: Session = SessionLocal()
    try:
        extractor = Extractor(TICKERS)
        
        if is_historical:
            raw_data = extractor.fetch_historical_data(period="1y", interval="1d")
        else:
            raw_data = extractor.fetch_latest_data()

        if raw_data is not None and not raw_data.empty:
            prices_df, metrics_df = Transformer.clean_and_transform(raw_data, is_multi_ticker=True)
            
            if prices_df is not None and metrics_df is not None:
                loader = Loader(db)
                p_rows = loader.load_prices(prices_df)
                m_rows = loader.load_metrics(metrics_df)
                rows_processed = p_rows + m_rows
                status = "SUCCESS"
            else:
                status = "FAILED"
                error_message = "Transformation returned None or empty data."
        else:
            status = "FAILED"
            error_message = "Extraction returned no data."

    except Exception as e:
        status = "FAILED"
        error_message = str(e)
        logger.error(f"Pipeline run failed: {e}")
    finally:
        # Log the run
        try:
            log_entry = PipelineLog(
                run_id=run_id,
                status=status,
                rows_processed=rows_processed,
                timestamp=start_time,
                error_message=error_message
            )
            db.merge(log_entry) # Use merge to handle existing PK if any
            db.commit()
            logger.info(f"Pipeline run completed with status {status}. Rows processed: {rows_processed}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to log pipeline execution: {e}")
        finally:
            db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Run every 15 minutes during market hours Mon-Fri
    trigger = CronTrigger(
        day_of_week='mon-fri',
        hour='9-16',
        minute='*/15'
    )
    
    scheduler.add_job(
        run_pipeline,
        trigger=trigger,
        kwargs={"is_historical": False},
        id="incremental_pipeline_job",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started.")
    
    # Optional: We could trigger a historical run on startup if the DB is empty
    # For now, we'll expose an endpoint to trigger it manually or let the user do it
    return scheduler
