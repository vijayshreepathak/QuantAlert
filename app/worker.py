import asyncio
import time
from sqlalchemy.orm import Session
from .database import SessionLocal
from .market_feed import start_market_feeds
from .alert_engine import alert_engine
from .config import settings


class AlertWorker:
    def __init__(self):
        self.is_running = False
        self.db: Session = None
    
    def get_db(self):
        """Get database session"""
        if not self.db:
            self.db = SessionLocal()
        return self.db
    
    async def price_update_callback(self, symbol: str, price, volume, exchange):
        """Callback for price updates from market feed"""
        print(f"Price update: {symbol} = ₹{price}")
        
        # Broadcast to WebSocket clients
        try:
            from .main import app
            await app.state.broadcast({
                "type": "price_update",
                "symbol": symbol,
                "price": float(price),
                "volume": volume,
                "exchange": exchange
            })
        except Exception as e:
            print(f"WebSocket broadcast error: {e}")
        
        try:
            # Process alerts for this symbol
            alert_engine.process_symbol_alerts(symbol, price, self.get_db())
        except Exception as e:
            print(f"Error processing alerts for {symbol}: {e}")
    
    async def start_market_feed(self):
        """Start market data feed"""
        await start_market_feeds(self.price_update_callback)
    
    async def process_alerts_loop(self):
        """Background loop to process all alerts"""
        while self.is_running:
            try:
                # Process all alerts
                alert_engine.process_all_alerts(self.get_db())
                
                # Wait 10 seconds before next check
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"Error in alert processing loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def start(self):
        """Start the worker"""
        self.is_running = True
        print("Starting AlertWorker...")
        
        # Start market feed and alert processing concurrently
        await asyncio.gather(
            self.start_market_feed(),
            self.process_alerts_loop()
        )
    
    def stop(self):
        """Stop the worker"""
        self.is_running = False
        if self.db:
            self.db.close()


# Global worker instance
worker = AlertWorker()


async def main():
    """Main entry point for the worker"""
    try:
        await worker.start()
    except KeyboardInterrupt:
        print("Shutting down worker...")
        worker.stop()
    except Exception as e:
        print(f"Worker error: {e}")
        worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
