from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import duckdb
import os
from .config import settings

# PostgreSQL setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DuckDB setup
def get_duckdb_connection():
    """Get DuckDB connection for market data"""
    # Use in-memory database for development to avoid file locking issues
    if settings.duckdb_path == "./data/market_data.duckdb":
        conn = duckdb.connect(":memory:")
    else:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(settings.duckdb_path), exist_ok=True)
        conn = duckdb.connect(settings.duckdb_path)
    
    # Initialize schema if not exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ticks (
            symbol VARCHAR(50),
            price DECIMAL(10, 2),
            volume BIGINT,
            timestamp TIMESTAMP,
            exchange VARCHAR(20)
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ohlcv_1min (
            symbol VARCHAR(50),
            open_price DECIMAL(10, 2),
            high_price DECIMAL(10, 2),
            low_price DECIMAL(10, 2),
            close_price DECIMAL(10, 2),
            volume BIGINT,
            timestamp TIMESTAMP,
            exchange VARCHAR(20)
        )
    """)
    
    # Create indexes
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ticks_symbol_timestamp ON ticks(symbol, timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_timestamp ON ohlcv_1min(symbol, timestamp)")
    
    return conn

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
