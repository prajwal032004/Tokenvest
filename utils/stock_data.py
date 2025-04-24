import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import random  # For demo purposes

# You would need to register with a data provider like Alpha Vantage, Quandl, or an Indian market-specific API
# This is a placeholder implementation

# In production, replace these with actual API calls
def get_nse_stock_price(symbol):
    """
    Get real-time stock price data for Indian stocks.
    In production, you would use a real API like NSE India, Yahoo Finance or a paid data provider.
    """
    try:
        # For demo purposes, we're using a placeholder
        # In production, replace with actual API call to NSE data provider
        
        # Example API call (replace with your provider):
        # response = requests.get(f"https://api.example.com/stocks/india/{symbol}", headers={"X-API-KEY": "your_api_key"})
        # data = response.json()
        
        # Demo data (for testing only)
        if symbol == "^NSEI":  # NIFTY 50
            base_price = 22500
        elif symbol == "^BSESN":  # SENSEX
            base_price = 74000
        elif symbol == "BANKNIFTY.NS":  # Bank NIFTY
            base_price = 48000
        elif symbol == "NIFTYIT.NS":  # NIFTY IT
            base_price = 36000
        else:
            # Random price for other stocks between 500 and 5000
            base_price = random.uniform(500, 5000)
        
        # Add some random fluctuation
        fluctuation = random.uniform(-2, 2) / 100  # -2% to +2%
        price = base_price * (1 + fluctuation)
        
        # Calculate change
        change = base_price * fluctuation
        change_percent = fluctuation * 100
        
        return {
            'symbol': symbol,
            'price': round(price, 2),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'volume': random.randint(100000, 5000000),
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"Error fetching stock price for {symbol}: {e}")
        raise

def get_nse_historical_data(symbol, period='1M'):
    """
    Get historical data for charting.
    period: 1D, 1W, 1M, 3M, 6M, 1Y, 5Y
    """
    try:
        # In production, replace with actual API call to data provider
        # Example: response = requests.get(f"https://api.example.com/historical/{symbol}?period={period}")
        
        # Demo data for testing
        end_date = datetime.now()
        
        if period == '1D':
            # Hourly data for one day
            start_date = end_date - timedelta(days=1)
            intervals = 24
            date_format = '%H:%M'
        elif period == '1W':
            # Daily data for one week
            start_date = end_date - timedelta(weeks=1)
            intervals = 7
            date_format = '%d %b'
        elif period == '1M':
            # Daily data for one month
            start_date = end_date - timedelta(days=30)
            intervals = 30
            date_format = '%d %b'
        elif period == '3M':
            # Daily data for three months
            start_date = end_date - timedelta(days=90)
            intervals = 90
            date_format = '%d %b'
        elif period == '6M':
            # Daily data for six months
            start_date = end_date - timedelta(days=180)
            intervals = 180
            date_format = '%d %b'
        elif period == '1Y':
            # Daily data for one year
            start_date = end_date - timedelta(days=365)
            intervals = 365
            date_format = '%d %b'
        else:  # 5Y
            # Monthly data for five years
            start_date = end_date - timedelta(days=365*5)
            intervals = 60  # Monthly for 5 years
            date_format = '%b %Y'
        
        # Generate demo data
        data = []
        
        if symbol == "^NSEI":  # NIFTY 50
            base_price = 22500
            volatility = 0.01  # 1% daily change
        elif symbol == "^BSESN":  # SENSEX
            base_price = 74000
            volatility = 0.01
        elif symbol == "BANKNIFTY.NS":  # Bank NIFTY
            base_price = 48000
            volatility = 0.015
        elif symbol == "NIFTYIT.NS":  # NIFTY IT
            base_price = 36000
            volatility = 0.012
        else:
            # Random price for other stocks
            base_price = random.uniform(500, 5000)
            volatility = random.uniform(0.01, 0.03)
        
        # Generate a simple random walk
        price = base_price
        time_delta = (end_date - start_date) / intervals
        
        for i in range(intervals):
            current_date = start_date + (i * time_delta)
            # Random walk with some trend bias
            change = np.random.normal(0.0002, volatility)  # Slight positive bias
            price = price * (1 + change)
            
            # Generate OHLC data
            open_price = price * (1 + np.random.normal(0, 0.002))
            high_price = price * (1 + abs(np.random.normal(0, 0.005)))
            low_price = price * (1 - abs(np.random.normal(0, 0.005)))
            close_price = price
            volume = int(np.random.normal(500000, 200000))
            
            data.append({
                'date': current_date.strftime(date_format),
                'timestamp': int(current_date.timestamp() * 1000),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
        
        return data
    
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        raise

def update_all_stock_prices(app):
    """
    Background task to update all stock prices in the database.
    """
    with app.app_context():
        from models import Stock, db
        
        stocks = Stock.query.all()
        for stock in stocks:
            try:
                live_data = get_nse_stock_price(stock.symbol)
                stock.full_price = live_data['price']
                stock.change_percent = live_data['change_percent']
                stock.token_price = calculate_token_price(live_data['price'], stock.token_count)
            except Exception as e:
                print(f"Error updating price for {stock.symbol}: {e}")
        
        db.session.commit()
        print(f"Updated all stock prices at {datetime.now()}")

def calculate_token_price(full_price, token_count):
    """
    Calculate token price based on full stock price and token count.
    """
    return full_price / token_count