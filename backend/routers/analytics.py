from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.database import get_db
from models.schemas import Stock, Price, Metric

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/top-movers")
def get_top_movers(db: Session = Depends(get_db)):
    """
    Gets the top gainers and losers based on the most recent data point.
    In a real app, this would use a more complex query joining current and previous day's close.
    For simplicity, we'll fetch the latest 2 records per ticker and calculate % change.
    """
    # A simplified approach for the dashboard
    tickers = db.query(Stock.ticker).all()
    results = []
    
    for (ticker,) in tickers:
        prices = db.query(Price).filter(Price.ticker == ticker).order_by(Price.date.desc()).limit(2).all()
        if len(prices) >= 2:
            current = prices[0].close
            previous = prices[1].close
            pct_change = ((current - previous) / previous) * 100
            results.append({
                "ticker": ticker,
                "current_price": current,
                "change_percent": pct_change
            })
            
    # Sort by change percent
    sorted_results = sorted(results, key=lambda x: x["change_percent"], reverse=True)
    
    return {
        "gainers": sorted_results[:5],
        "losers": sorted_results[-5:][::-1] if len(sorted_results) > 5 else []
    }

@router.get("/summary")
def get_market_summary(db: Session = Depends(get_db)):
    """
    Returns basic DB stats.
    """
    total_stocks = db.query(func.count(Stock.ticker)).scalar()
    total_prices = db.query(func.count(Price.id)).scalar()
    return {
        "tracked_stocks": total_stocks,
        "total_data_points": total_prices
    }
