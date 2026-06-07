from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from models.schemas import Stock, Price, Metric

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("/")
def get_all_stocks(db: Session = Depends(get_db)):
    stocks = db.query(Stock).all()
    return stocks

@router.get("/{ticker}")
def get_stock_details(ticker: str, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.ticker == ticker.upper()).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # Get latest price
    latest_price = db.query(Price).filter(Price.ticker == ticker.upper()).order_by(Price.date.desc()).first()
    
    return {
        "stock": stock,
        "latest_price": latest_price
    }

@router.get("/{ticker}/history")
def get_stock_history(ticker: str, limit: int = 100, db: Session = Depends(get_db)):
    prices = db.query(Price).filter(Price.ticker == ticker.upper()).order_by(Price.date.desc()).limit(limit).all()
    # Return chronologically
    return prices[::-1]

@router.get("/{ticker}/metrics")
def get_stock_metrics(ticker: str, limit: int = 100, db: Session = Depends(get_db)):
    metrics = db.query(Metric).filter(Metric.ticker == ticker.upper()).order_by(Metric.date.desc()).limit(limit).all()
    return metrics[::-1]
