"""
Simple Mock Market Feed
Works immediately - no API keys or external dependencies needed!
"""

import asyncio
import random
from decimal import Decimal
from typing import Callable
from datetime import datetime
import logging
from .market_data import market_data

logger = logging.getLogger(__name__)

class SimpleMockFeed:
    """Simple mock market feed that works immediately"""
    
    def __init__(self):
        self.symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        self.base_prices = {
            "RELIANCE": Decimal("2500.00"),
            "TCS": Decimal("3800.00"),
            "INFY": Decimal("1500.00"),
            "HDFCBANK": Decimal("1600.00"),
            "ICICIBANK": Decimal("950.00")
        }
        self.price_callback = None
        self.is_running = False
    
    def set_price_callback(self, callback: Callable):
        """Set callback function for price updates"""
        self.price_callback = callback
    
    async def start_feed(self):
        """Start the simple mock feed"""
        self.is_running = True
        logger.info("Starting Simple Mock Feed (no API keys needed!)")
        
        while self.is_running:
            try:
                for symbol in self.symbols:
                    # Generate realistic price movement
                    base_price = self.base_prices[symbol]
                    change_percent = random.uniform(-1, 1)  # ±1% change
                    new_price = base_price * Decimal(str(1 + change_percent / 100))
                    volume = random.randint(1000, 10000)
                    
                    # Update base price
                    self.base_prices[symbol] = new_price
                    
                    # Store in market data
                    market_data.store_tick(symbol, new_price, volume, "NSE")
                    market_data.update_ohlcv_1min(symbol, new_price, volume, "NSE")
                    
                    # Call callback if set
                    if self.price_callback:
                        await self.price_callback(symbol, new_price, volume, "NSE")
                    
                    logger.info(f"Simple Mock: {symbol} = ₹{new_price:.2f}")
                
                # Wait 10 seconds before next update
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Simple mock feed error: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    def stop_feed(self):
        """Stop the feed"""
        self.is_running = False
        logger.info("Stopped Simple Mock Feed")

# Global instance
simple_feed = SimpleMockFeed()
