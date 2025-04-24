from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Added index for faster lookups
    password_hash = db.Column(db.String(256), nullable=False)  # Increased length for stronger hashing
    balance = db.Column(db.Float, default=10000.0, nullable=False)  # Starting with ₹10,000
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    holdings = db.relationship('Holding', backref='user', lazy='dynamic')  # Changed to dynamic for query flexibility
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')

    def __repr__(self):
        return f"<User {self.email}>"

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(20), unique=True, nullable=False, index=True)  # Added index for faster lookups
    description = db.Column(db.Text, nullable=True)
    sector = db.Column(db.String(100), nullable=True)
    full_price = db.Column(db.Float, nullable=False)
    token_count = db.Column(db.Integer, nullable=False, default=100)  # Default to 100 tokens per share
    token_price = db.Column(db.Float, nullable=False)
    change_percent = db.Column(db.Float, default=0.0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Added to enable/disable stocks
    
    # Relationships
    tokens = db.relationship('Token', backref='stock', lazy='dynamic')
    holdings = db.relationship('Holding', backref='stock', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='stock', lazy='dynamic')

    def __repr__(self):
        return f"<Stock {self.symbol}>"

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Added index for faster lookups
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Added to track token status

    def __repr__(self):
        return f"<Token {self.token_id}>"

class Holding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # Added index
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False, index=True)  # Added index
    token_quantity = db.Column(db.Integer, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'stock_id', name='unique_user_stock'),
    )

    def __repr__(self):
        return f"<Holding user_id={self.user_id}, stock_id={self.stock_id}>"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # Added index
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False, index=True)  # Added index
    tokens = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'BUY' or 'SELL'
    price = db.Column(db.Float, nullable=False)  # Price per token at transaction time
    fee = db.Column(db.Float, default=0.0, nullable=False)  # Added for transaction fees
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Computed property for total value
    @property
    def total_value(self):
        return self.tokens * self.price + self.fee

    def __repr__(self):
        return f"<Transaction {self.type} {self.tokens} tokens>"