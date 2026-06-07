-- Initialize schema

CREATE TABLE IF NOT EXISTS stocks (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    exchange VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(10),
    date DATETIME,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    UNIQUE KEY ticker_date_idx (ticker, date),
    FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(10),
    date DATETIME,
    sma_7 FLOAT,
    sma_30 FLOAT,
    rsi FLOAT,
    volatility FLOAT,
    vwap FLOAT,
    UNIQUE KEY ticker_date_idx (ticker, date),
    FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pipeline_logs (
    run_id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20),
    rows_processed INT,
    timestamp DATETIME,
    error_message TEXT
);

-- Seed basic stocks
INSERT IGNORE INTO stocks (ticker, company_name, sector, exchange) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'NASDAQ'),
('GOOGL', 'Alphabet Inc.', 'Technology', 'NASDAQ'),
('MSFT', 'Microsoft Corporation', 'Technology', 'NASDAQ'),
('TSLA', 'Tesla, Inc.', 'Automotive', 'NASDAQ'),
('AMZN', 'Amazon.com, Inc.', 'Consumer Cyclical', 'NASDAQ'),
('META', 'Meta Platforms, Inc.', 'Technology', 'NASDAQ'),
('NVDA', 'NVIDIA Corporation', 'Technology', 'NASDAQ'),
('JPM', 'JPMorgan Chase & Co.', 'Financial Services', 'NYSE'),
('V', 'Visa Inc.', 'Financial Services', 'NYSE'),
('JNJ', 'Johnson & Johnson', 'Healthcare', 'NYSE');
