"""
Angel Broking Market Data Feed
"""

import asyncio
import json
import websockets
import aiohttp
from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging
from .config import settings

logger = logging.getLogger(__name__)

class AngelBrokingFeed:
    """Angel Broking WebSocket feed for real-time market data"""
    
    def __init__(self):
        self.api_key = settings.angel_api_key
        self.client_id = settings.angel_client_id
        self.password = settings.angel_password
        self.feed_token = settings.angel_feed_token
        
        # WebSocket URLs
        self.ws_url = "wss://smartapis.angelone.in/websocket"
        self.api_url = "https://apiconnect.angelbroking.com"
        
        self.ws_connection = None
        self.is_connected = False
        self.price_callback = None
        
        # Common symbols mapping
        self.symbols = {
            "RELIANCE": "RELIANCE-EQ",
            "TCS": "TCS-EQ", 
            "HDFCBANK": "HDFCBANK-EQ",
            "INFY": "INFY-EQ",
            "ICICIBANK": "ICICIBANK-EQ",
            "HINDUNILVR": "HINDUNILVR-EQ",
            "ITC": "ITC-EQ",
            "SBIN": "SBIN-EQ",
            "BHARTIARTL": "BHARTIARTL-EQ",
            "KOTAKBANK": "KOTAKBANK-EQ"
        }
    
    async def authenticate(self) -> bool:
        """Authenticate with Angel Broking API"""
        if not all([self.api_key, self.client_id, self.password]):
            logger.error("Missing Angel Broking credentials")
            return False
        
        try:
            auth_url = f"{self.api_url}/rest/auth/angelbroking/user/v1/loginByPassword"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-UserType": "USER",
                "X-SourceID": "WEB",
                "X-ClientLocalIP": "CLIENT_LOCAL_IP",
                "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
                "X-MACAddress": "MAC_ADDRESS",
                "X-PrivateKey": self.api_key
            }
            
            payload = {
                "clientcode": self.client_id,
                "password": self.password,
                "totp": ""
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") and data.get("data", {}).get("jwtToken"):
                            self.feed_token = data["data"]["jwtToken"]
                            logger.info("Angel Broking authentication successful")
                            return True
                        else:
                            logger.error(f"Authentication failed: {data}")
                            return False
                    else:
                        logger.error(f"Authentication request failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def connect_websocket(self):
        """Connect to Angel Broking WebSocket"""
        if not self.feed_token:
            if not await self.authenticate():
                return False
        
        try:
            self.ws_connection = await websockets.connect(self.ws_url)
            self.is_connected = True
            logger.info("Connected to Angel Broking WebSocket")
            
            # Send subscription message
            await self.subscribe_symbols()
            
            # Start listening for messages
            await self.listen_messages()
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            self.is_connected = False
            return False
    
    async def subscribe_symbols(self):
        """Subscribe to symbol feeds"""
        if not self.is_connected:
            return
        
        try:
            # Subscribe to LTP (Last Traded Price) for symbols
            subscription_data = {
                "actiontype": "subscribe",
                "feedtype": "ltp",
                "jwttoken": self.feed_token,
                "clientcode": self.client_id,
                "tokens": list(self.symbols.values())
            }
            
            await self.ws_connection.send(json.dumps(subscription_data))
            logger.info(f"Subscribed to {len(self.symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Subscription error: {e}")
    
    async def listen_messages(self):
        """Listen for incoming WebSocket messages"""
        try:
            async for message in self.ws_connection:
                await self.process_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            self.is_connected = False
    
    async def process_message(self, message: str):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            # Handle different message types
            if "ltp" in data:
                await self.handle_ltp_data(data["ltp"])
            elif "error" in data:
                logger.error(f"WebSocket error: {data['error']}")
            elif "message" in data:
                logger.info(f"WebSocket message: {data['message']}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
        except Exception as e:
            logger.error(f"Message processing error: {e}")
    
    async def handle_ltp_data(self, ltp_data: Dict):
        """Handle LTP (Last Traded Price) data"""
        try:
            for token_data in ltp_data:
                symbol = token_data.get("symbol")
                price = token_data.get("ltp", 0)
                timestamp = datetime.now()
                
                if symbol and price and self.price_callback:
                    # Convert Angel symbol to standard symbol
                    standard_symbol = self.get_standard_symbol(symbol)
                    if standard_symbol:
                        await self.price_callback(standard_symbol, price, timestamp)
                        
        except Exception as e:
            logger.error(f"LTP data processing error: {e}")
    
    def get_standard_symbol(self, angel_symbol: str) -> Optional[str]:
        """Convert Angel Broking symbol to standard symbol"""
        for std_symbol, angel_sym in self.symbols.items():
            if angel_sym == angel_symbol:
                return std_symbol
        return None
    
    def set_price_callback(self, callback: Callable):
        """Set callback function for price updates"""
        self.price_callback = callback
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.ws_connection:
            await self.ws_connection.close()
            self.is_connected = False
            logger.info("Disconnected from Angel Broking WebSocket")
    
    async def start(self, price_callback: Callable):
        """Start the Angel Broking feed"""
        self.set_price_callback(price_callback)
        await self.connect_websocket()

# Global instance
angel_feed = AngelBrokingFeed()
