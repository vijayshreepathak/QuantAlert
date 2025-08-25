#!/usr/bin/env python3
"""
QuantAlert Web Application Startup
Beautiful web interface with real-time market data and alerts
"""

import asyncio
import subprocess
import sys
import time
import os
from pathlib import Path

def create_data_directory():
    """Create data directory if it doesn't exist"""
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Data directory ready: {data_dir.absolute()}")

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("⚠️  No .env file found. Creating from template...")
        if Path("env_local.txt").exists():
            import shutil
            shutil.copy("env_local.txt", ".env")
            print("✅ Created .env file from template")
        else:
            print("❌ No env_local.txt template found")
            return False
    
    print("✅ Environment configuration ready")
    return True

def initialize_database():
    """Initialize the database tables"""
    print("🗄️  Initializing database...")
    try:
        # Import and create tables
        from app.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def start_api():
    """Start the FastAPI server"""
    print("🚀 Starting QuantAlert Web Application...")
    print("📋 What's happening:")
    print("1. ✅ No API keys needed!")
    print("2. ✅ Simple mock data provides real-time prices")
    print("3. ✅ Beautiful web interface at: http://localhost:8000")
    print("4. ✅ Real-time WebSocket updates")
    print("5. ✅ Email alerts (configure SMTP in .env)")
    
    try:
        # Start uvicorn with reload
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        return process
    except Exception as e:
        print(f"❌ Failed to start API: {e}")
        return None

def start_worker():
    """Start the background worker"""
    print("🔄 Starting background worker...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "app.worker"
        ])
        return process
    except Exception as e:
        print(f"❌ Failed to start worker: {e}")
        return None

def main():
    print("🎯 QuantAlert Web Application")
    print("=" * 50)
    
    # Setup
    create_data_directory()
    
    if not check_environment():
        print("❌ Environment setup failed")
        return
    
    if not initialize_database():
        print("❌ Database setup failed")
        return
    
    # Start services
    print("\n🚀 Starting services...")
    api_process = start_api()
    
    if not api_process:
        print("❌ Failed to start API")
        return
    
    # Wait for API to start
    time.sleep(3)
    
    worker_process = start_worker()
    
    if not worker_process:
        print("❌ Failed to start worker")
        api_process.terminate()
        return
    
    print("\n✅ QuantAlert Web Application is running!")
    print("🌐 Web Interface: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\n💡 Features:")
    print("• Real-time market data (mock data)")
    print("• Create and manage price alerts")
    print("• Email notifications")
    print("• Beautiful responsive web interface")
    print("• WebSocket real-time updates")
    print("\n🛑 To stop: Press Ctrl+C")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        api_process.terminate()
        worker_process.terminate()
        print("✅ Services stopped")

if __name__ == "__main__":
    main()
