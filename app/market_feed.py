import asyncio
import websockets
import json
import aiohttp
from decimal import Decimal
from typing import Dict, List, Optional, Callable
from .market_data import market_data
from .config import settings
from .angel_feed import angel_feed
from .yahoo_feed import yahoo_feed
from .alpha_vantage_feed import alpha_vantage_feed
from .simple_feed import simple_feed


class MarketFeed:
    def __init__(self):
        self.websocket = None
        self.is_connected = False
        self.symbols = []
        self.price_callback: Optional[Callable] = None
    
    async def connect_openalgo(self, symbols: List[str]):
        """Connect to OpenAlgo WebSocket feed"""
        if not settings.openalgo_api_key:
            raise ValueError("OpenAlgo API key not configured")
        
        uri = f"wss://ws.openalgo.in/feed?api_key={settings.openalgo_api_key}"
        
        try:
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            
            # Subscribe to symbols
            subscribe_msg = {
                "action": "subscribe",
                "symbols": symbols
            }
            await self.websocket.send(json.dumps(subscribe_msg))
            
            print(f"Connected to OpenAlgo feed for {len(symbols)} symbols")
            
        except Exception as e:
            print(f"Failed to connect to OpenAlgo: {e}")
            raise
    
    async def connect_upstox(self, symbols: List[str]):
        """Connect to Upstox WebSocket feed"""
        if not settings.upstox_api_key:
            raise ValueError("Upstox API key not configured")
        
        uri = f"wss://ws-api.upstox.com/index"
        
        try:
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            
            # Subscribe to symbols
            subscribe_msg = {
                "action": "subscribe",
                "symbols": symbols,
                "api_key": settings.upstox_api_key
            }
            await self.websocket.send(json.dumps(subscribe_msg))
            
            print(f"Connected to Upstox feed for {len(symbols)} symbols")
            
        except Exception as e:
            print(f"Failed to connect to Upstox: {e}")
            raise
    
    async def connect_dhan(self, symbols: List[str]):
        """Connect to Dhan WebSocket feed"""
        if not settings.dhan_api_key:
            raise ValueError("Dhan API key not configured")
        
        uri = f"wss://stream.dhan.co/feed"
        
        try:
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            
            # Subscribe to symbols
            subscribe_msg = {
                "action": "subscribe",
                "symbols": symbols,
                "api_key": settings.dhan_api_key
            }
            await self.websocket.send(json.dumps(subscribe_msg))
            
            print(f"Connected to Dhan feed for {len(symbols)} symbols")
            
        except Exception as e:
            print(f"Failed to connect to Dhan: {e}")
            raise
    
    def set_price_callback(self, callback: Callable):
        """Set callback function for price updates"""
        self.price_callback = callback
    
    async def process_message(self, message: str):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            # Handle different message formats from different providers
            if "symbol" in data and "price" in data:
                # OpenAlgo format
                symbol = data["symbol"]
                price = Decimal(str(data["price"]))
                volume = data.get("volume", 0)
                exchange = data.get("exchange", "NSE")
                
                # Store in market data
                market_data.store_tick(symbol, price, volume, exchange)
                market_data.update_ohlcv_1min(symbol, price, volume, exchange)
                
                # Call callback if set
                if self.price_callback:
                    await self.price_callback(symbol, price, volume, exchange)
                
                print(f"Price update: {symbol} = ₹{price}")
            
            elif "ltp" in data and "symbol" in data:
                # Upstox format
                symbol = data["symbol"]
                price = Decimal(str(data["ltp"]))
                volume = data.get("volume", 0)
                
                market_data.store_tick(symbol, price, volume, "NSE")
                market_data.update_ohlcv_1min(symbol, price, volume, "NSE")
                
                if self.price_callback:
                    await self.price_callback(symbol, price, volume, "NSE")
                
                print(f"Price update: {symbol} = ₹{price}")
            
            elif "data" in data:
                # Dhan format
                for item in data["data"]:
                    if "symbol" in item and "ltp" in item:
                        symbol = item["symbol"]
                        price = Decimal(str(item["ltp"]))
                        volume = item.get("volume", 0)
                        
                        market_data.store_tick(symbol, price, volume, "NSE")
                        market_data.update_ohlcv_1min(symbol, price, volume, "NSE")
                        
                        if self.price_callback:
                            await self.price_callback(symbol, price, volume, "NSE")
                        
                        print(f"Price update: {symbol} = ₹{price}")
        
        except json.JSONDecodeError:
            print(f"Invalid JSON message: {message}")
        except Exception as e:
            print(f"Error processing message: {e}")
    
    async def listen(self):
        """Listen for WebSocket messages"""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        try:
            async for message in self.websocket:
                await self.process_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            print(f"WebSocket error: {e}")
            self.is_connected = False
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            print("Disconnected from market feed")


# Mock market data for testing
class MockMarketFeed:
    """Mock market feed for testing without real market data"""
    
    def __init__(self):
        self.symbols = ["RELIANCE", "TCS", "INFY", "HDFC", "ICICIBANK"]
        self.base_prices = {
            "RELIANCE": Decimal("2500.00"),
            "TCS": Decimal("3800.00"),
            "INFY": Decimal("1500.00"),
            "HDFC": Decimal("1600.00"),
            "ICICIBANK": Decimal("950.00")
        }
        self.price_callback = None
    
    def set_price_callback(self, callback: Callable):
        self.price_callback = callback
    
    async def start_mock_feed(self):
        """Start mock price feed with random price movements"""
        import random
        
        while True:
            for symbol in self.symbols:
                # Generate random price movement
                base_price = self.base_prices[symbol]
                change_percent = random.uniform(-2, 2)  # ±2% change
                new_price = base_price * (1 + change_percent / 100)
                volume = random.randint(1000, 10000)
                
                # Update base price
                self.base_prices[symbol] = new_price
                
                # Store in market data
                market_data.store_tick(symbol, new_price, volume, "NSE")
                market_data.update_ohlcv_1min(symbol, new_price, volume, "NSE")
                
                # Call callback if set
                if self.price_callback:
                    await self.price_callback(symbol, new_price, volume, "NSE")
                
                print(f"Mock price update: {symbol} = ₹{new_price:.2f}")
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)


# Global instance
market_feed = MarketFeed()
mock_feed = MockMarketFeed()

async def start_market_feeds(price_callback):
    """Start market data feeds by configured provider or fallback"""
    provider = getattr(settings, 'feed_provider', 'auto')

    async def start_simple():
        simple_feed.set_price_callback(price_callback)
        await simple_feed.start_feed()
        print("Started Simple Mock Feed (works immediately!)")

    async def start_yahoo():
        yahoo_feed.set_price_callback(price_callback)
        await yahoo_feed.start_feed()
        print("Started Yahoo Finance feed (no API key required!)")

    async def start_alpha():
        alpha_vantage_feed.set_price_callback(price_callback)
        await alpha_vantage_feed.start_feed()
        print("Started Alpha Vantage feed")

    if provider == 'simple':
        try:
            return await start_simple()
        except Exception as e:
            print(f"Simple mock feed failed: {e}")
    elif provider == 'yahoo':
        try:
            return await start_yahoo()
        except Exception as e:
            print(f"Yahoo Finance feed failed: {e}")
    elif provider == 'alpha_vantage':
        try:
            return await start_alpha()
        except Exception as e:
            print(f"Alpha Vantage feed failed: {e}")
    elif provider == 'angel':
        if settings.angel_api_key and settings.angel_client_id:
            try:
                await angel_feed.start(price_callback)
                print("Started Angel Broking feed")
                return
            except Exception as e:
                print(f"Angel Broking feed failed: {e}")
    # auto fallback order
    try:
        return await start_simple()
    except Exception as e:
        print(f"Simple mock feed failed: {e}")
    try:
        return await start_yahoo()
    except Exception as e:
        print(f"Yahoo Finance feed failed: {e}")
    if hasattr(settings, 'alpha_vantage_api_key') and settings.alpha_vantage_api_key:
        try:
            return await start_alpha()
        except Exception as e:
            print(f"Alpha Vantage feed failed: {e}")
    if settings.openalgo_api_key:
        try:
            await market_feed.connect_openalgo(["RELIANCE", "TCS", "INFY", "HDFC", "ICICIBANK"])
            market_feed.set_price_callback(price_callback)
            await market_feed.listen()
            return
        except Exception as e:
            print(f"OpenAlgo feed failed: {e}")
    if settings.upstox_api_key:
        try:
            await market_feed.connect_upstox(["RELIANCE", "TCS", "INFY", "HDFC", "ICICIBANK"])
            market_feed.set_price_callback(price_callback)
            await market_feed.listen()
            return
        except Exception as e:
            print(f"Upstox feed failed: {e}")
    if settings.dhan_api_key:
        try:
            await market_feed.connect_dhan(["RELIANCE", "TCS", "INFY", "HDFC", "ICICIBANK"])
            market_feed.set_price_callback(price_callback)
            await market_feed.listen()
            return
        except Exception as e:
            print(f"Dhan feed failed: {e}")
    print("No real market feeds available, using fallback mock data")
    mock_feed.set_price_callback(price_callback)
    await mock_feed.start_mock_feed()
