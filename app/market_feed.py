# app/market_feed.py
import asyncio
import inspect
from .config import settings
from .yahoo_feed import yahoo_feed

async def start_market_feeds(price_callback):
    """Start market data feeds - Yahoo Finance ONLY (no simple_feed)"""
    
    # Ensure callback works with both sync/async
    async def safe_callback(*args):
        if inspect.iscoroutinefunction(price_callback):
            await price_callback(*args)
        else:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, price_callback, *args)
    
    provider = getattr(settings, 'feed_provider', 'yahoo')
    print(f"🔥 Starting market feed provider: {provider}")
    
    # ONLY Yahoo Finance - no mock feeds
    try:
        yahoo_feed.set_price_callback(safe_callback)
        await yahoo_feed.start_feed(poll_seconds=8)
        print("✅ Yahoo Finance feed started successfully")
    except Exception as e:
        print(f"❌ Yahoo Finance failed: {e}")
        raise RuntimeError("Yahoo feed failed")
