"""
Yahoo Finance Market Data Feed
No API key required - completely free!
"""

import asyncio
import aiohttp
import json
from decimal import Decimal
from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging
from .market_data import market_data

logger = logging.getLogger(__name__)

class YahooFinanceFeed:
    """Yahoo Finance market data feed - No API key required!"""
    
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.price_callback = None
        self.is_running = False
        
        # Indian stocks with .NS suffix for NSE
        self.symbols = {
            "RELIANCE": "RELIANCE.NS",
            "TCS": "TCS.NS", 
            "HDFCBANK": "HDFCBANK.NS",
            "INFY": "INFY.NS",
            "ICICIBANK": "ICICIBANK.NS",
            "HINDUNILVR": "HINDUNILVR.NS",
            "ITC": "ITC.NS",
            "SBIN": "SBIN.NS",
            "BHARTIARTL": "BHARTIARTL.NS",
            "KOTAKBANK": "KOTAKBANK.NS"
        }
    
    def set_price_callback(self, callback: Callable):
        """Set callback function for price updates"""
        self.price_callback = callback
    
    async def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest price for a symbol"""
        try:
            yahoo_symbol = self.symbols.get(symbol)
            if not yahoo_symbol:
                return None
            
            url = f"{self.base_url}/{yahoo_symbol}"
            params = {
                "interval": "1m",
                "range": "1d"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract latest price
                        if "chart" in data and "result" in data["chart"]:
                            result = data["chart"]["result"][0]
                            if "meta" in result:
                                price = result["meta"].get("regularMarketPrice")
                                if price:
                                    return float(price)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    async def fetch_all_prices(self):
        """Fetch prices for all symbols"""
        tasks = []
        for symbol in self.symbols.keys():
            task = self.get_latest_price(symbol)
            tasks.append((symbol, task))
        
        for symbol, task in tasks:
            try:
                price = await task
                if price and self.price_callback:
                    volume = 1000  # Default volume for Yahoo Finance
                    await self.price_callback(symbol, Decimal(str(price)), volume, "NSE")
                    logger.info(f"Yahoo Finance: {symbol} = ₹{price}")
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
    
    async def start_feed(self):
        """Start the Yahoo Finance feed"""
        self.is_running = True
        logger.info("Starting Yahoo Finance feed...")
        
        while self.is_running:
            try:
                await self.fetch_all_prices()
                # Wait 30 seconds before next update (Yahoo Finance rate limit)
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Yahoo Finance feed error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def stop_feed(self):
        """Stop the feed"""
        self.is_running = False
        logger.info("Stopped Yahoo Finance feed")

# Global instance
yahoo_feed = YahooFinanceFeed()
