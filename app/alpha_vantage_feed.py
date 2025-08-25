"""
Alpha Vantage Market Data Feed
Free tier available - 5 API calls per minute
"""

import asyncio
import aiohttp
import json
from decimal import Decimal
from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging
from .market_data import market_data
from .config import settings

logger = logging.getLogger(__name__)

class AlphaVantageFeed:
    """Alpha Vantage market data feed - Free tier available"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'alpha_vantage_api_key', None)
        self.base_url = "https://www.alphavantage.co/query"
        self.price_callback = None
        self.is_running = False
        
        # Indian stocks (Alpha Vantage uses different symbols)
        self.symbols = {
            "RELIANCE": "RELIANCE.BSE",
            "TCS": "TCS.BSE", 
            "HDFCBANK": "HDFCBANK.BSE",
            "INFY": "INFY.BSE",
            "ICICIBANK": "ICICIBANK.BSE",
            "HINDUNILVR": "HINDUNILVR.BSE",
            "ITC": "ITC.BSE",
            "SBIN": "SBIN.BSE",
            "BHARTIARTL": "BHARTIARTL.BSE",
            "KOTAKBANK": "KOTAKBANK.BSE"
        }
    
    def set_price_callback(self, callback: Callable):
        """Set callback function for price updates"""
        self.price_callback = callback
    
    async def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest price for a symbol"""
        if not self.api_key:
            logger.warning("Alpha Vantage API key not configured")
            return None
        
        try:
            alpha_symbol = self.symbols.get(symbol)
            if not alpha_symbol:
                return None
            
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": alpha_symbol,
                "apikey": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract latest price
                        if "Global Quote" in data:
                            quote = data["Global Quote"]
                            price = quote.get("05. price")
                            if price:
                                return float(price)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    async def fetch_all_prices(self):
        """Fetch prices for all symbols (respecting rate limits)"""
        for symbol in self.symbols.keys():
            try:
                price = await self.get_latest_price(symbol)
                if price and self.price_callback:
                    volume = 1000  # Default volume
                    await self.price_callback(symbol, Decimal(str(price)), volume, "BSE")
                    logger.info(f"Alpha Vantage: {symbol} = ₹{price}")
                
                # Wait 12 seconds between calls (5 calls per minute = 12 seconds each)
                await asyncio.sleep(12)
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
    
    async def start_feed(self):
        """Start the Alpha Vantage feed"""
        if not self.api_key:
            logger.error("Alpha Vantage API key not configured")
            return
        
        self.is_running = True
        logger.info("Starting Alpha Vantage feed...")
        
        while self.is_running:
            try:
                await self.fetch_all_prices()
                # Wait 1 minute before next cycle (respect rate limits)
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Alpha Vantage feed error: {e}")
                await asyncio.sleep(120)  # Wait longer on error
    
    def stop_feed(self):
        """Stop the feed"""
        self.is_running = False
        logger.info("Stopped Alpha Vantage feed")

# Global instance
alpha_vantage_feed = AlphaVantageFeed()
