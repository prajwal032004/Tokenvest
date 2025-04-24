from datetime import datetime
import uuid

def create_tokens(stock_id, token_count):
    """
    Create tokens for a stock.
    In a real implementation, this could involve blockchain or other tokenization methods.
    """
    from models import db, Token
    
    tokens = []
    for i in range(token_count):
        token_id = f"{stock_id}-{uuid.uuid4()}"
        new_token = Token(
            token_id=token_id,
            stock_id=stock_id,
            created_at=datetime.now()
        )
        tokens.append(new_token)
    
    db.session.add_all(tokens)
    db.session.commit()
    
    return tokens

def calculate_token_price(stock_price, token_count):
    """
    Calculate the price of a single token based on the full stock price
    and the number of tokens.
    """
    if token_count <= 0:
        return 0
    
    return round(stock_price / token_count, 2)