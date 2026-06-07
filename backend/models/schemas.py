from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Stock(Base):
    __tablename__ = "stocks"

    ticker = Column(String(10), primary_key=True, index=True)
    company_name = Column(String(255))
    sector = Column(String(100))
    exchange = Column(String(50))

    prices = relationship("Price", back_populates="stock", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="stock", cascade="all, delete-orphan")

class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (UniqueConstraint('ticker', 'date', name='uq_prices_ticker_date'),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker", ondelete="CASCADE"), index=True)
    date = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

    stock = relationship("Stock", back_populates="prices")

class Metric(Base):
    __tablename__ = "metrics"
    __table_args__ = (UniqueConstraint('ticker', 'date', name='uq_metrics_ticker_date'),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker", ondelete="CASCADE"), index=True)
    date = Column(DateTime, index=True)
    sma_7 = Column(Float)
    sma_30 = Column(Float)
    rsi = Column(Float)
    volatility = Column(Float)
    vwap = Column(Float)

    stock = relationship("Stock", back_populates="metrics")

class PipelineLog(Base):
    __tablename__ = "pipeline_logs"

    run_id = Column(String(50), primary_key=True, index=True)
    status = Column(String(20))
    rows_processed = Column(Integer)
    timestamp = Column(DateTime)
    error_message = Column(Text, nullable=True)
