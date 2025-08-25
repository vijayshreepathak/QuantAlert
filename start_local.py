#!/usr/bin/env python3
"""
Local startup script for QuantAlert without Docker
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
        if Path("env.example").exists():
            import shutil
            shutil.copy("env.example", ".env")
            print("✅ Created .env file. Please edit it with your API keys.")
        else:
            print("❌ No env.example found. Please create .env file manually.")
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
    print("🎯 QuantAlert Local Startup")
    print("=" * 50)
    
    # Create data directory
    create_data_directory()
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please fix the issues above.")
        return
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your market data API keys")
    print("2. The system will use mock data if no API keys are provided")
    print("3. API will be available at: http://localhost:8000")
    print("4. API docs at: http://localhost:8000/docs")
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
    
    print("\n✅ QuantAlert is running!")
    print("📊 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔍 Health: http://localhost:8000/health")
    print("\n💡 To stop: Press Ctrl+C")
    
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
