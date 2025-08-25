import duckdb
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from .database import get_duckdb_connection
from .schemas import PriceData, OHLCVData


class MarketDataManager:
    def __init__(self):
        self.conn = get_duckdb_connection()
    
    def store_tick(self, symbol: str, price: Decimal, volume: int, exchange: str = "NSE"):
        """Store a tick data point"""
        timestamp = datetime.now()
        
        self.conn.execute("""
            INSERT INTO ticks (symbol, price, volume, timestamp, exchange)
            VALUES (?, ?, ?, ?, ?)
        """, [symbol, float(price), volume, timestamp, exchange])
    
    def get_latest_price(self, symbol: str) -> Optional[PriceData]:
        """Get the latest price for a symbol"""
        result = self.conn.execute("""
            SELECT symbol, price, volume, timestamp, exchange
            FROM ticks
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, [symbol]).fetchone()
        
        if result:
            return PriceData(
                symbol=result[0],
                price=Decimal(str(result[1])),
                volume=result[2],
                timestamp=result[3],
                exchange=result[4]
            )
        return None
    
    def get_ohlcv_1min(self, symbol: str, minutes: int = 60) -> List[OHLCVData]:
        """Get 1-minute OHLCV data for the last N minutes"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=minutes)
        
        result = self.conn.execute("""
            SELECT symbol, open_price, high_price, low_price, close_price, volume, timestamp, exchange
            FROM ohlcv_1min
            WHERE symbol = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        """, [symbol, start_time, end_time]).fetchall()
        
        return [
            OHLCVData(
                symbol=row[0],
                open_price=Decimal(str(row[1])),
                high_price=Decimal(str(row[2])),
                low_price=Decimal(str(row[3])),
                close_price=Decimal(str(row[4])),
                volume=row[5],
                timestamp=row[6],
                exchange=row[7]
            )
            for row in result
        ]
    
    def update_ohlcv_1min(self, symbol: str, current_price: Decimal, volume: int, exchange: str = "NSE"):
        """Update 1-minute OHLCV data with new tick"""
        current_time = datetime.now()
        minute_start = current_time.replace(second=0, microsecond=0)
        
        # Check if we have data for this minute
        existing = self.conn.execute("""
            SELECT open_price, high_price, low_price, close_price, volume
            FROM ohlcv_1min
            WHERE symbol = ? AND timestamp = ?
        """, [symbol, minute_start]).fetchone()
        
        if existing:
            # Update existing minute data
            open_price = existing[0]
            high_price = max(existing[1], float(current_price))
            low_price = min(existing[2], float(current_price))
            close_price = float(current_price)
            total_volume = existing[4] + volume
            
            self.conn.execute("""
                UPDATE ohlcv_1min
                SET high_price = ?, low_price = ?, close_price = ?, volume = ?
                WHERE symbol = ? AND timestamp = ?
            """, [high_price, low_price, close_price, total_volume, symbol, minute_start])
        else:
            # Create new minute data
            self.conn.execute("""
                INSERT INTO ohlcv_1min (symbol, open_price, high_price, low_price, close_price, volume, timestamp, exchange)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [symbol, float(current_price), float(current_price), float(current_price), float(current_price), volume, minute_start, exchange])
    
    def get_all_symbols(self) -> List[str]:
        """Get all unique symbols in the database"""
        result = self.conn.execute("""
            SELECT DISTINCT symbol FROM ticks
            UNION
            SELECT DISTINCT symbol FROM ohlcv_1min
        """).fetchall()
        
        return [row[0] for row in result]
    
    def close(self):
        """Close the database connection"""
        self.conn.close()


# Global instance
market_data = MarketDataManager()
