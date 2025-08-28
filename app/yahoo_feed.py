from __future__ import annotations

import asyncio
import inspect
import logging
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Callable, Dict, Optional, Tuple

import yfinance as yf

logger = logging.getLogger(__name__)


def _q2(value) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class YahooFinanceFeed:
    """
    Robust Yahoo Finance poller with freshness checks:
      1) fast_info.last_price (or dict keys)
      2) info['regularMarketPrice'] / 'currentPrice'
      3) last 1m bar Close if bar is fresh (<= freshness_secs)
    Emits only fresh prices to avoid stale updates.
    """

    def __init__(self):
        self.symbols: Dict[str, str] = {
            "RELIANCE": "RELIANCE.NS",
            "TCS": "TCS.NS",
            "HDFCBANK": "HDFCBANK.NS",
            "INFY": "INFY.NS",
            "ICICIBANK": "ICICIBANK.NS",
            "HINDUNILVR": "HINDUNILVR.NS",
            "ITC": "ITC.NS",
            "SBIN": "SBIN.NS",
            "BHARTIARTL": "BHARTIARTL.NS",
            "KOTAKBANK": "KOTAKBANK.NS",
        }
        self.price_callback: Optional[Callable] = None
        self.is_running = False
        self.poll_seconds = 30
        # Treat bars newer than this threshold as “live enough”
        self.freshness_secs = 90

    def set_price_callback(self, callback: Callable):
        self.price_callback = callback

    async def _invoke_callback(self, *args):
        if not self.price_callback:
            return
        cb = self.price_callback
        if inspect.iscoroutinefunction(cb):
            await cb(*args)
        else:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, cb, *args)

    def _fetch_sync(self, friendly: str, y_sym: str) -> Tuple[str, Optional[Decimal], int]:
        """
        Return (name, price_decimal_or_None, volume_int).
        Only returns a value considered 'fresh'; otherwise (name, None, 0).
        """
        t = yf.Ticker(y_sym)

        # 1) fast_info
        price = None
        volume = 0
        fi = getattr(t, "fast_info", None)
        if fi is not None:
            try:
                # attribute-style
                price = getattr(fi, "last_price", None)
                if price is None and isinstance(fi, dict):
                    # dict-style across yfinance versions
                    price = fi.get("last_price") or fi.get("lastPrice")
                if isinstance(fi, dict):
                    volume = int(fi.get("last_volume") or fi.get("lastVolume") or 0)
                else:
                    volume = int(getattr(fi, "last_volume", 0) or 0)
            except Exception:
                price = None
                volume = 0

        # 2) info fallback (may be delayed)
        if price is None:
            try:
                info = t.info or {}
                price = info.get("regularMarketPrice") or info.get("currentPrice")
                volume = int(info.get("regularMarketVolume") or info.get("volume") or 0)
            except Exception:
                price = None

        # If we got a number, emit it; still may be delayed but better than nothing
        if price is not None:
            return friendly, _q2(price), volume

        # 3) last 1-minute bar as a fresh snapshot
        try:
            # Include pre/post in case of extended sessions; NSE typically regular
            df = yf.download(y_sym, period="1d", interval="1m", prepost=True, progress=False)
            if df is not None and not df.empty and "Close" in df.columns:
                last_ts = df.index[-1].to_pydatetime()
                # Ensure timezone-aware comparison
                if last_ts.tzinfo is None:
                    last_ts = last_ts.replace(tzinfo=timezone.utc)
                age = (_utc_now() - last_ts).total_seconds()
                if age <= self.freshness_secs:
                    last_close = float(df["Close"].iloc[-1])
                    last_vol = int(df["Volume"].iloc[-1] if "Volume" in df.columns else 0)
                    return friendly, _q2(last_close), last_vol
                else:
                    logger.debug("Stale 1m bar for %s (age=%.1fs), suppressing", friendly, age)
        except Exception as e:
            logger.error("1m fallback error for %s: %s", friendly, e)

        # Nothing fresh
        return friendly, None, 0

    async def _fetch_one(self, friendly: str, y_sym: str):
        try:
            return await asyncio.to_thread(self._fetch_sync, friendly, y_sym)
        except Exception as e:
            logger.error("Fetch error for %s: %s", friendly, e)
            return friendly, None, 0

    async def fetch_all_prices(self):
        tasks = [self._fetch_one(f, y) for f, y in self.symbols.items()]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        for friendly, price, volume in results:
            if price is None:
                # Explicitly skip stale values to avoid “wrong” price updates
                continue
            try:
                await self._invoke_callback(friendly, price, int(volume or 0), "NSE")
            except Exception as e:
                logger.error("price_callback error for %s: %s", friendly, e)
            logger.info("Yahoo fresh: %s = ₹%s", friendly, price)

    async def start_feed(self, poll_seconds: int = 30, freshness_secs: int = 90):
        self.is_running = True
        self.poll_seconds = poll_seconds
        self.freshness_secs = freshness_secs
        logger.info("Starting Yahoo Finance feed (poll=%ss, freshness=%ss)...", poll_seconds, freshness_secs)
        while self.is_running:
            try:
                await self.fetch_all_prices()
                await asyncio.sleep(self.poll_seconds)
            except Exception as e:
                logger.error("Yahoo feed loop error: %s", e)
                await asyncio.sleep(max(30, self.poll_seconds))

    def stop_feed(self):
        self.is_running = False
        logger.info("Stopped Yahoo Finance feed")


# Global instance
yahoo_feed = YahooFinanceFeed()
