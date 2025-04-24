from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import json
import requests
import pandas as pd
import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler

from models import db, User, Stock, Token, Holding, Transaction
from utils.stock_data import get_nse_stock_price, get_nse_historical_data, update_all_stock_prices
from utils.token_engine import create_tokens, calculate_token_price

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Set up background task for updating stock prices
scheduler = BackgroundScheduler()
scheduler.add_job(func=lambda: update_all_stock_prices(app), trigger="interval", minutes=5)
scheduler.start()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    # Get market indices for homepage
    try:
        nifty_data = get_nse_stock_price("^NSEI")
        sensex_data = get_nse_stock_price("^BSESN")
        nifty_bank = get_nse_stock_price("BANKNIFTY.NS")
        market_data = {
            'nifty': nifty_data,
            'sensex': sensex_data,
            'nifty_bank': nifty_bank
        }
    except Exception as e:
        print(f"Error fetching market data: {e}")
        market_data = {}
        
    return render_template('index.html', market_data=market_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(name=name, email=email, 
                       password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
                       balance=10000.0)  # Starting with ₹10000 for demo
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get top stocks for the dashboard
    stocks = Stock.query.limit(10).all()
    user_holdings = Holding.query.filter_by(user_id=current_user.id).all()
    
    # Update live prices
    for stock in stocks:
        try:
            live_price = get_nse_stock_price(stock.symbol)
            stock.full_price = live_price['price']
            stock.change_percent = live_price['change_percent']
            stock.token_price = calculate_token_price(live_price['price'], stock.token_count)
        except Exception as e:
            print(f"Error updating price for {stock.symbol}: {e}")
    
    db.session.commit()
    
    # Get market overview for dashboard
    try:
        nifty_data = get_nse_stock_price("^NSEI")
        sensex_data = get_nse_stock_price("^BSESN")
        market_data = {
            'nifty': nifty_data,
            'sensex': sensex_data
        }
    except Exception as e:
        print(f"Error fetching market data: {e}")
        market_data = {}
    
    # Calculate portfolio summary
    portfolio_value = 0
    for holding in user_holdings:
        stock = Stock.query.get(holding.stock_id)
        portfolio_value += holding.token_quantity * stock.token_price
    
    return render_template('dashboard.html', 
                          stocks=stocks, 
                          holdings=user_holdings, 
                          market_data=market_data,
                          portfolio_value=portfolio_value)

@app.route('/stock/<symbol>')
@login_required
def stock_detail(symbol):
    stock = Stock.query.filter_by(symbol=symbol).first_or_404()
    try:
        live_data = get_nse_stock_price(symbol)
        stock.full_price = live_data['price']
        stock.change_percent = live_data['change_percent']
        stock.token_price = calculate_token_price(live_data['price'], stock.token_count)
        db.session.commit()
    except Exception as e:
        print(f"Error fetching live price: {e}")
        
    # Get historical data for charts
    try:
        historical_data = get_nse_historical_data(symbol)
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        historical_data = []
        
    # Get recent transactions for this stock
    transactions = Transaction.query.filter_by(stock_id=stock.id).order_by(Transaction.date.desc()).limit(10).all()
    
    # Get user holding for this stock
    holding = Holding.query.filter_by(user_id=current_user.id, stock_id=stock.id).first()
    
    return render_template('stock_detail.html', 
                          stock=stock,
                          holding=holding,
                          historical_data=json.dumps(historical_data),
                          transactions=transactions)

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    # Fetch only active stocks
    stocks = Stock.query.filter_by(is_active=True).all()
    if not stocks:
        flash('No stocks available for purchase.', 'error')
        return render_template('buy.html', stocks=[])
    
    if request.method == 'POST':
        stock_id = request.form.get('stock_id')
        token_quantity = request.form.get('token_quantity')
        try:
            stock_id = int(stock_id)
            token_quantity = int(token_quantity)
            if token_quantity <= 0:
                flash('Token quantity must be positive.', 'error')
                return redirect(url_for('buy'))
            stock = Stock.query.get_or_404(stock_id)
            if not stock.is_active:
                flash('Selected stock is not available for purchase.', 'error')
                return redirect(url_for('buy'))
            # Fetch live price
            try:
                live_data = get_nse_stock_price(stock.symbol)
                stock.full_price = live_data['price']
                stock.token_price = calculate_token_price(live_data['price'], stock.token_count)
                stock.change_percent = live_data['change_percent']
                stock.last_updated = datetime.now()
                db.session.commit()
            except Exception as e:
                flash(f'Error fetching live price: {e}', 'error')
                return redirect(url_for('buy'))
            total_cost = stock.token_price * token_quantity
            transaction_fee = total_cost * 0.01  # Example: 1% fee
            if current_user.balance >= (total_cost + transaction_fee):
                current_user.balance -= (total_cost + transaction_fee)
                holding = Holding.query.filter_by(user_id=current_user.id, stock_id=stock.id).first()
                if holding:
                    holding.token_quantity += token_quantity
                    holding.last_updated = datetime.now()
                else:
                    holding = Holding(user_id=current_user.id, stock_id=stock.id, token_quantity=token_quantity)
                transaction = Transaction(
                    user_id=current_user.id,
                    stock_id=stock.id,
                    tokens=token_quantity,
                    type='BUY',
                    price=stock.token_price,
                    fee=transaction_fee,
                    date=datetime.now()
                )
                db.session.add(holding)
                db.session.add(transaction)
                db.session.commit()
                flash(f'Successfully purchased {token_quantity} tokens of {stock.name}', 'message')
                return redirect(url_for('portfolio'))
            else:
                flash('Insufficient balance.', 'error')
        except ValueError:
            flash('Invalid input.', 'error')
        return redirect(url_for('buy'))
    return render_template('buy.html', stocks=stocks)

@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    if request.method == 'POST':
        stock_id = request.form.get('stock_id')
        token_quantity = int(request.form.get('token_quantity'))
        
        stock = Stock.query.get_or_404(stock_id)
        holding = Holding.query.filter_by(user_id=current_user.id, stock_id=stock.id).first_or_404()
        
        # Get latest price
        try:
            live_data = get_nse_stock_price(stock.symbol)
            stock.full_price = live_data['price']
            stock.token_price = calculate_token_price(live_data['price'], stock.token_count)
            db.session.commit()
        except Exception as e:
            flash(f'Error fetching latest price: {e}')
            return redirect(url_for('sell'))
        
        # Check if user has enough tokens
        if holding.token_quantity < token_quantity:
            flash('Insufficient tokens')
            return redirect(url_for('sell'))
        
        # Calculate return amount
        return_amount = token_quantity * stock.token_price
        
        # Update user balance
        current_user.balance += return_amount
        
        # Update holding
        holding.token_quantity -= token_quantity
        
        # Remove holding if zero tokens left
        if holding.token_quantity == 0:
            db.session.delete(holding)
        
        # Record transaction
        transaction = Transaction(
            user_id=current_user.id,
            stock_id=stock.id,
            tokens=token_quantity,
            type='SELL',
            price=stock.token_price,
            date=datetime.now()
        )
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Successfully sold {token_quantity} tokens of {stock.name}')
        return redirect(url_for('portfolio'))
    
    # Get user holdings for sell options
    holdings = Holding.query.filter_by(user_id=current_user.id).all()
    stocks = {}
    
    for holding in holdings:
        stock = Stock.query.get(holding.stock_id)
        try:
            live_data = get_nse_stock_price(stock.symbol)
            stock.full_price = live_data['price']
            stock.token_price = calculate_token_price(live_data['price'], stock.token_count)
        except Exception as e:
            print(f"Error updating price for {stock.symbol}: {e}")
        stocks[holding.stock_id] = stock
    
    db.session.commit()
    
    return render_template('sell.html', holdings=holdings, stocks=stocks)

@app.route('/portfolio')
@login_required
def portfolio():
    holdings = Holding.query.filter_by(user_id=current_user.id).all()
    
    portfolio_value = 0
    portfolio_items = []
    
    for holding in holdings:
        stock = Stock.query.get(holding.stock_id)
        
        try:
            live_data = get_nse_stock_price(stock.symbol)
            stock.full_price = live_data['price']
            stock.change_percent = live_data['change_percent']
            stock.token_price = calculate_token_price(live_data['price'], stock.token_count)
            db.session.commit()
        except Exception as e:
            print(f"Error updating price for {stock.symbol}: {e}")
        
        value = holding.token_quantity * stock.token_price
        portfolio_value += value
        
        portfolio_items.append({
            'stock': stock,
            'tokens': holding.token_quantity,
            'value': value
        })
    
    # Get transaction history for portfolio
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(10).all()
    
    return render_template('portfolio.html', 
                          portfolio_items=portfolio_items,
                          portfolio_value=portfolio_value,
                          transactions=transactions)

@app.route('/market')
@login_required
def market():
    # Fetch NSE top gainers and losers
    try:
        top_gainers = get_nse_top_gainers()
        top_losers = get_nse_top_losers()
    except Exception as e:
        print(f"Error fetching market data: {e}")
        top_gainers = []
        top_losers = []
        
    return render_template('market.html', 
                          top_gainers=top_gainers,
                          top_losers=top_losers)

@app.route('/transactions')
@login_required
def transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    
    # Add stock information to each transaction
    total_buy_amount = 0
    for transaction in transactions:
        transaction.stock_name = Stock.query.get(transaction.stock_id).name
        transaction.stock_symbol = Stock.query.get(transaction.stock_id).symbol
        
        # Calculate the total amount for each buy transaction
        if transaction.type == 'BUY':
            total_buy_amount += transaction.price * transaction.tokens
    
    return render_template('transactions.html', 
                          transactions=transactions,
                          total_buy_amount=total_buy_amount)

# API Routes for charts and data
@app.route('/api/stock/<symbol>/history')
def stock_history_api(symbol):
    # Get period from request, default to 1M (one month)
    period = request.args.get('period', '1M')
    
    try:
        data = get_nse_historical_data(symbol, period)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>/price')
def stock_price_api(symbol):
    try:
        data = get_nse_stock_price(symbol)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/indices')
def market_indices_api():
    try:
        nifty = get_nse_stock_price("^NSEI")
        sensex = get_nse_stock_price("^BSESN")
        nifty_bank = get_nse_stock_price("BANKNIFTY.NS")
        nifty_it = get_nse_stock_price("NIFTYIT.NS")
        
        return jsonify({
            'nifty': nifty,
            'sensex': sensex,
            'nifty_bank': nifty_bank,
            'nifty_it': nifty_it
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_nse_top_gainers():
    # In production, you would fetch this from an actual API
    # This is a placeholder implementation
    try:
        # Simulate top gainers - in production replace with actual API call
        stocks = Stock.query.all()
        gainers = []
        
        for stock in stocks:
            try:
                live_data = get_nse_stock_price(stock.symbol)
                if live_data['change_percent'] > 0:
                    gainers.append({
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'price': live_data['price'],
                        'change_percent': live_data['change_percent']
                    })
            except Exception:
                continue
        
        # Sort by change percent in descending order and take top 5
        gainers.sort(key=lambda x: x['change_percent'], reverse=True)
        return gainers[:5]
    except Exception as e:
        print(f"Error fetching top gainers: {e}")
        return []

def get_nse_top_losers():
    # In production, you would fetch this from an actual API
    # This is a placeholder implementation
    try:
        # Simulate top losers - in production replace with actual API call
        stocks = Stock.query.all()
        losers = []
        
        for stock in stocks:
            try:
                live_data = get_nse_stock_price(stock.symbol)
                if live_data['change_percent'] < 0:
                    losers.append({
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'price': live_data['price'],
                        'change_percent': live_data['change_percent']
                    })
            except Exception:
                continue
        
        # Sort by change percent in ascending order and take top 5
        losers.sort(key=lambda x: x['change_percent'])
        return losers[:5]
    except Exception as e:
        print(f"Error fetching top losers: {e}")
        return []

# Admin routes (would be restricted in production)
@app.route('/admin/add_stock', methods=['GET', 'POST'])
@login_required
def add_stock():
    if request.method == 'POST':
        name = request.form.get('name')
        symbol = request.form.get('symbol')
        token_count = int(request.form.get('token_count'))
        
        # Get initial price from NSE
        try:
            live_data = get_nse_stock_price(symbol)
            price = live_data['price']
        except Exception as e:
            flash(f'Could not get price for symbol {symbol}: {e}')
            return redirect(url_for('add_stock'))
        
        new_stock = Stock(
            name=name,
            symbol=symbol,
            full_price=price,
            token_count=token_count,
            token_price=calculate_token_price(price, token_count)
        )
        
        db.session.add(new_stock)
        db.session.commit()
        
        # Create tokens for this stock
        create_tokens(new_stock.id, token_count)
        
        flash(f'Added {name} with {token_count} tokens')
        return redirect(url_for('dashboard'))
    
    return render_template('add_stock.html')

@app.route('/admin/stocks')
@login_required
def admin_stocks():
    stocks = Stock.query.all()
    return render_template('admin_stocks.html', stocks=stocks)

# Teardown context for scheduler
@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    if scheduler.running:
        scheduler.shutdown()

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)