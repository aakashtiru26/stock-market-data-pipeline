const API_BASE_URL = 'http://localhost:8000';
let stockChartInstance = null;
let currentTicker = 'AAPL';

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    
    // Refresh loop every 60 seconds
    setInterval(refreshData, 60000);

    // Event Listeners
    document.getElementById('stock-selector').addEventListener('change', (e) => {
        currentTicker = e.target.value;
        loadStockData(currentTicker);
    });

    document.getElementById('btn-refresh').addEventListener('click', refreshData);
    document.getElementById('btn-trigger-pipeline').addEventListener('click', triggerPipeline);
});

async function initDashboard() {
    await fetchStocks();
    await refreshData();
}

async function refreshData() {
    await loadPipelineStatus();
    await loadMarketSummary();
    await loadTopMovers();
    if(currentTicker) {
        await loadStockData(currentTicker);
    }
}

async function fetchStocks() {
    try {
        const res = await fetch(`${API_BASE_URL}/stocks/`);
        const stocks = await res.json();
        
        const selector = document.getElementById('stock-selector');
        selector.innerHTML = '<option value="" disabled>Select Ticker</option>';
        
        stocks.forEach(stock => {
            const option = document.createElement('option');
            option.value = stock.ticker;
            option.textContent = `${stock.ticker} - ${stock.company_name}`;
            if(stock.ticker === currentTicker) option.selected = true;
            selector.appendChild(option);
        });
    } catch (e) {
        console.error('Error fetching stocks:', e);
    }
}

async function loadStockData(ticker) {
    try {
        // Fetch Details + Latest Price
        const detailsRes = await fetch(`${API_BASE_URL}/stocks/${ticker}`);
        const details = await detailsRes.json();
        
        // Fetch History
        const historyRes = await fetch(`${API_BASE_URL}/stocks/${ticker}/history?limit=30`);
        const history = await historyRes.json();

        // Fetch Metrics
        const metricsRes = await fetch(`${API_BASE_URL}/stocks/${ticker}/metrics?limit=30`);
        const metrics = await metricsRes.json();

        updateMetricsCards(details, history);
        renderChart(history, metrics);
        
    } catch (e) {
        console.error('Error loading stock data:', e);
    }
}

function updateMetricsCards(details, history) {
    if(details.latest_price) {
        document.getElementById('metric-price').textContent = `$${details.latest_price.close.toFixed(2)}`;
        document.getElementById('metric-volume').textContent = details.latest_price.volume.toLocaleString();
        
        if(history.length >= 2) {
            const current = history[history.length - 1].close;
            const prev = history[history.length - 2].close;
            const change = ((current - prev) / prev) * 100;
            
            const changeEl = document.getElementById('metric-change');
            changeEl.textContent = `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
            changeEl.className = change >= 0 ? 'positive' : 'negative';
        }
    }
}

function renderChart(history, metrics) {
    const ctx = document.getElementById('stockChart').getContext('2d');
    
    if (stockChartInstance) {
        stockChartInstance.destroy();
    }

    const labels = history.map(item => new Date(item.date).toLocaleDateString());
    const prices = history.map(item => item.close);
    const sma7 = metrics.map(item => item.sma_7);
    const sma30 = metrics.map(item => item.sma_30);

    stockChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Close Price',
                    data: prices,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'SMA 7',
                    data: sma7,
                    borderColor: '#10b981',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: 'SMA 30',
                    data: sma30,
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    borderDash: [2, 2],
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#f8fafc' } }
            },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
            }
        }
    });

    // Update RSI Metric Card
    if(metrics.length > 0) {
        const latestRsi = metrics[metrics.length-1].rsi;
        document.getElementById('metric-rsi').textContent = latestRsi ? latestRsi.toFixed(2) : '-';
    }
}

async function loadPipelineStatus() {
    try {
        const res = await fetch(`${API_BASE_URL}/pipeline/status`);
        const status = await res.json();
        
        const indicator = document.getElementById('pipeline-status-indicator');
        if(status.status) {
            document.getElementById('pipeline-last-run').textContent = `Last Run: ${new Date(status.timestamp).toLocaleString()}`;
            document.getElementById('pipeline-rows').textContent = `Rows Processed: ${status.rows_processed}`;
            
            indicator.className = 'status-indicator';
            if(status.status === 'SUCCESS') indicator.classList.add('success');
            else if(status.status === 'FAILED') indicator.classList.add('failed');
            else indicator.classList.add('running');
        }
    } catch (e) {
        console.error('Error fetching pipeline status:', e);
    }
}

async function loadMarketSummary() {
    try {
        const res = await fetch(`${API_BASE_URL}/analytics/summary`);
        const summary = await res.json();
        document.getElementById('summary-stocks').textContent = summary.tracked_stocks;
        document.getElementById('summary-points').textContent = summary.total_data_points;
    } catch (e) {
        console.error('Error fetching summary:', e);
    }
}

async function loadTopMovers() {
    try {
        const res = await fetch(`${API_BASE_URL}/analytics/top-movers`);
        const data = await res.json();
        
        const populateTable = (tableId, items, isGainer) => {
            const tbody = document.getElementById(tableId).querySelector('tbody');
            tbody.innerHTML = '';
            items.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.ticker}</strong></td>
                    <td>$${item.current_price.toFixed(2)}</td>
                    <td class="${isGainer ? 'positive' : 'negative'}">${isGainer ? '+' : ''}${item.change_percent.toFixed(2)}%</td>
                `;
                tbody.appendChild(tr);
            });
        };

        populateTable('gainers-table', data.gainers, true);
        populateTable('losers-table', data.losers, false);
    } catch (e) {
        console.error('Error fetching top movers:', e);
    }
}

async function triggerPipeline() {
    try {
        await fetch(`${API_BASE_URL}/pipeline/trigger?is_historical=false`, { method: 'POST' });
        alert('Pipeline triggered. Wait a few moments and refresh data.');
        setTimeout(loadPipelineStatus, 3000);
    } catch (e) {
        console.error('Error triggering pipeline:', e);
    }
}
