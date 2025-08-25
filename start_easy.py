#!/usr/bin/env python3
"""
Easy startup script for QuantAlert with Yahoo Finance (No API keys needed!)
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
            print("✅ Created .env file.")
        else:
            print("❌ No env_local.txt found. Please create .env file manually.")
            return False
    
    print("✅ Environment configuration ready")
    return True

def start_api():
    """Start the FastAPI server"""
    print("🚀 Starting QuantAlert API...")
    try:
        # Start API server
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
        # Start worker
        process = subprocess.Popen([
            sys.executable, "-m", "app.worker"
        ])
        return process
    except Exception as e:
        print(f"❌ Failed to start worker: {e}")
        return None

def main():
    """Main startup function"""
    print("🎯 QuantAlert Easy Startup (Yahoo Finance)")
    print("=" * 50)
    
    # Create data directory
    create_data_directory()
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please fix the issues above.")
        return
    
    print("\n📋 What's happening:")
    print("1. ✅ No API keys needed!")
    print("2. ✅ Yahoo Finance will provide real market data")
    print("3. ✅ API will be available at: http://localhost:8000")
    print("4. ✅ API docs at: http://localhost:8000/docs")
    print("\n🚀 Starting services...")
    
    # Start API
    api_process = start_api()
    if not api_process:
        return
    
    # Wait a moment for API to start
    time.sleep(3)
    
    # Start worker
    worker_process = start_worker()
    if not worker_process:
        api_process.terminate()
        return
    
    print("\n✅ QuantAlert is running with Yahoo Finance!")
    print("📊 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔍 Health: http://localhost:8000/health")
    print("\n💡 To stop: Press Ctrl+C")
    print("\n🎯 Next steps:")
    print("1. Visit http://localhost:8000/docs to see the API")
    print("2. Create alerts and watch for real-time updates")
    print("3. Check the logs for price updates every 30 seconds")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        api_process.terminate()
        worker_process.terminate()
        print("✅ Services stopped")

if __name__ == "__main__":
    main()
