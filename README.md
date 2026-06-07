# Stock Market Data Pipeline System

An end-to-end ETL (Extract, Transform, Load) pipeline that collects historical and near real-time stock market data, calculates key trading metrics, and serves the data through a FastAPI backend and an interactive web dashboard.

## 🏗 Architecture Overview

1. **Data Extraction**: Periodically fetches OHLCV (Open, High, Low, Close, Volume) data for tracked stock tickers using the `yfinance` library. 
2. **Data Transformation**: Cleans data and uses Pandas to calculate technical indicators:
   - Simple Moving Averages (7-day and 30-day)
   - Relative Strength Index (RSI - 14 period)
   - Annualized Volatility
   - Volume Weighted Average Price (VWAP)
3. **Data Loading**: Loads the raw prices and computed metrics into a normalized MySQL database using SQLAlchemy, handling duplicates with 'UPSERT' operations.
4. **Orchestration**: Runs as a background task within the FastAPI app using `APScheduler`, running incrementally every 15 minutes during market hours.
5. **Backend**: FastAPI REST service exposing endpoints to query stock history, metrics, and pipeline status.
6. **Frontend**: A responsive, dark-themed vanilla JS/HTML/CSS dashboard utilizing `Chart.js` for data visualization.

## 🚀 Setup Instructions

### Prerequisites
- Docker and Docker Compose

### Running the Application

1. **Clone the repository** (or navigate to the directory).
2. **Set up Environment Variables**:
   Copy the sample env file:
   ```bash
   cp .env.example .env
   ```
   *Modify the credentials inside `.env` if necessary.*

3. **Start the Docker Containers**:
   ```bash
   docker-compose up -d --build
   ```

4. **Verify Database Initialization**:
   On the first run, the MySQL container will initialize the schema from `schema.sql` and seed the `stocks` table.

5. **Trigger the Initial Data Load**:
   Since the scheduler runs every 15 minutes, you can manually trigger a historical load to see data immediately:
   ```bash
   curl -X POST "http://localhost:8000/pipeline/trigger?is_historical=true"
   ```

6. **Access the Application**:
   - **Backend API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Frontend Dashboard**: Open `frontend/index.html` directly in your browser.

## 📡 API Endpoints

### Stocks
- `GET /stocks/`: List all tracked stocks.
- `GET /stocks/{ticker}`: Get stock details and the latest price.
- `GET /stocks/{ticker}/history?limit=100`: Get historical OHLCV data.
- `GET /stocks/{ticker}/metrics?limit=100`: Get calculated metrics (SMA, RSI, etc.).

### Pipeline Control
- `GET /pipeline/status`: Get the status of the last pipeline run.
- `POST /pipeline/trigger?is_historical=false`: Manually trigger the pipeline in the background.

### Analytics
- `GET /analytics/top-movers`: Get the top 5 gainers and losers.
- `GET /analytics/summary`: Get a summary of tracked stocks and total data points.

## 🖼 Sample Screenshots

The frontend provides a sleek glassmorphism design:
- **Left Panel**: Shows the current pipeline execution status (Running/Success/Failed) and high-level market summary.
- **Top Row**: Shows key metrics for the selected stock (Current Price, Daily Change, Volume, RSI).
- **Center**: An interactive Chart.js canvas plotting the Close Price alongside the 7-day and 30-day Simple Moving Averages.
- **Bottom Section**: Two tables showing the top gaining and losing stocks based on the latest data fetch.
