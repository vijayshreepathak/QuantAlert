from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
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
    raw_path = settings.duckdb_path or ":memory:"
    # Normalize quotes around special value
    duckdb_path = str(raw_path).strip().strip('"\'')
    if duckdb_path == ":memory:":
        # Use in-memory database to avoid file locking issues inside containers
        conn = duckdb.connect(":memory:")
    else:
        # If a file path is provided, ensure directory exists, fall back to memory if locked
        dir_name = os.path.dirname(duckdb_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        try:
            conn = duckdb.connect(duckdb_path)
        except duckdb.duckdb.IOException:
            # Fallback when file is locked by another process (e.g., Docker vs local)
            conn = duckdb.connect(":memory:")
    
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


def _ensure_sqlite_migrations():
    """Ensure SQLite DB has latest columns for existing tables.
    This keeps local quantalert.db compatible after schema updates.
    """
    if not settings.database_url.startswith("sqlite"):
        return
    try:
        with engine.begin() as conn:
            # Check alert_rules table
            cols = conn.execute(text("PRAGMA table_info('alert_rules')")).fetchall()
            col_names = {row[1] for row in cols}  # (cid, name, type, ...)
            if 'data_source' not in col_names:
                conn.execute(text("ALTER TABLE alert_rules ADD COLUMN data_source VARCHAR(20) NOT NULL DEFAULT 'tick'"))
            if 'column_name' not in col_names:
                conn.execute(text("ALTER TABLE alert_rules ADD COLUMN column_name VARCHAR(20) NOT NULL DEFAULT 'price'"))
            if 'ohlcv_timeframe_minutes' not in col_names:
                conn.execute(text("ALTER TABLE alert_rules ADD COLUMN ohlcv_timeframe_minutes INTEGER NOT NULL DEFAULT 1"))
    except Exception:
        # Best-effort; avoid blocking app startup for local DBs
        pass


# Apply lightweight migrations for local SQLite
_ensure_sqlite_migrations()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
