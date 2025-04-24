from app import app, db
from models import Stock
from datetime import datetime

stocks = [
    Stock(
        symbol='RELIANCE.NS',
        name='Reliance Industries',
        description='Diversified conglomerate in energy, telecom, and retail.',
        sector='Conglomerate',
        full_price=3000.0,
        token_count=100,
        token_price=30.0,
        change_percent=2.5,
        is_active=True,
        last_updated=datetime.now()
    ),
    Stock(
        symbol='TCS.NS',
        name='Tata Consultancy Services',
        description='Leading IT services provider specializing in digital transformation.',
        sector='Information Technology',
        full_price=4000.0,
        token_count=100,
        token_price=40.0,
        change_percent=1.8,
        is_active=True,
        last_updated=datetime.now()
    ),
    Stock(
        symbol='ICICIBANK.NS',
        name='ICICI Bank',
        description='Major private bank with strong digital banking services.',
        sector='Banking',
        full_price=1200.0,
        token_count=100,
        token_price=12.0,
        change_percent=2.0,
        is_active=True,
        last_updated=datetime.now()
    ),
    Stock(
        symbol='BAJFINANCE.NS',
        name='Bajaj Finance',
        description='Leading NBFC focused on consumer finance and lending.',
        sector='Financial Services',
        full_price=7000.0,
        token_count=100,
        token_price=70.0,
        change_percent=3.1,
        is_active=True,
        last_updated=datetime.now()
    ),
    Stock(
        symbol='HAL.NS',
        name='Hindustan Aeronautics',
        description='PSU specializing in aerospace and defense manufacturing.',
        sector='Aerospace & Defense',
        full_price=4000.0,
        token_count=100,
        token_price=40.0,
        change_percent=4.5,
        is_active=True,
        last_updated=datetime.now()
    )
]

with app.app_context():
    db.session.bulk_save_objects(stocks)
    db.session.commit()
    print("Stocks added successfully!")