# TokenVest

TokenVest is a fractional stock ownership platform that allows users to invest in Indian equities with minimal capital by purchasing tokens representing partial shares.

## 📈 About TokenVest

TokenVest democratizes investing by tokenizing stocks from the National Stock Exchange (NSE) of India. Each stock is divided into multiple tokens, allowing investors to purchase fractions of shares with lower capital requirements. This model makes premium stocks with high share prices accessible to retail investors.

### Key Features

- **Fractional Stock Ownership**: Buy tokens representing partial shares of NSE-listed companies
- **Real-time Market Data**: Live stock prices, market indices, and historical data
- **Portfolio Management**: Track your holdings, transaction history, and portfolio performance
- **User-friendly Interface**: Simple buy/sell experience for beginner investors
- **Low Investment Threshold**: Start investing with as little as ₹100

## 🚀 Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login
- **Market Data**: NSE API integration
- **Background Tasks**: APScheduler

## 🛠️ Installation

1. Clone the repository:
   ```
   git clone https://github.com/prajwal032004/Tokenvest.git
   cd tokenvest
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a config file (`config.py`):
   ```python
   class Config:
       SECRET_KEY = 'your-secret-key'
       SQLALCHEMY_DATABASE_URI = 'sqlite:///tokenvest.db'
       SQLALCHEMY_TRACK_MODIFICATIONS = False
   ```

5. Initialize the database:
   ```
   flask shell
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Access the platform at http://localhost:9000

## 📊 How It Works

1. **Stock Tokenization**: Each stock is divided into a predefined number of tokens
2. **Token Price Calculation**: Token price = Full stock price ÷ Number of tokens
3. **Purchase Process**: Users buy tokens at the current market-derived token price
4. **Real-time Updates**: Token prices update dynamically with market movements
5. **Portfolio Valuation**: User portfolios are valued based on current token prices

## 📱 User Journey

1. **Register**: Create an account with email and password
2. **Fund**: Each user starts with ₹10,000 demo balance
3. **Browse**: Explore available stocks and market data
4. **Buy**: Purchase tokens of desired stocks
5. **Monitor**: Track portfolio performance on the dashboard
6. **Sell**: Liquidate tokens when desired

## 📋 Project Structure

```
tokenvest/
├── app.py                # Main application file
├── config.py             # Configuration settings
├── models/               # Database models
│   ├── __init__.py
│   └── models.py
├── utils/                # Utility functions
│   ├── stock_data.py     # Stock data fetching functions
│   └── token_engine.py   # Token creation and pricing logic
├── static/               # Static assets (CSS, JS, images)
├── templates/            # HTML templates
     
```

## 🔍 API Endpoints

The platform provides several API endpoints for frontend interaction:

- `/api/stock/<symbol>/history` - Get historical price data for a stock
- `/api/stock/<symbol>/price` - Get current price for a stock
- `/api/market/indices` - Get current market indices data

## 🛣️ Roadmap

- [ ] Mobile app development
- [ ] Integration with payment gateways
- [ ] Social trading features
- [ ] Dividend distribution system
- [ ] Advanced charting tools
- [ ] API for third-party integrations

## 💡 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the TokenVest copyright License.

**Disclaimer**: TokenVest is a demonstration project and not a real investment platform. It does not use real money or execute actual trades on the stock market. Any resemblance to real trading platforms is coincidental.
