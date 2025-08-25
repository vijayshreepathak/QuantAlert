#!/usr/bin/env python3
"""
Test script for QuantAlert system
Run this after starting the services to verify everything works
"""

import asyncio
import requests
import json
from decimal import Decimal
import time

# Configuration
API_BASE = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_health():
    """Test API health endpoint"""
    print("Testing API health...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def test_registration():
    """Test user registration"""
    print("Testing user registration...")
    try:
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        response = requests.post(f"{API_BASE}/register", json=data)
        if response.status_code == 200:
            print("✅ User registered successfully")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("✅ User already exists (expected)")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login():
    """Test user login and get token"""
    print("Testing user login...")
    try:
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        response = requests.post(f"{API_BASE}/token", data=data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful")
            return token_data["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_market_data(token):
    """Test market data endpoints"""
    print("Testing market data endpoints...")
    
    # Test symbols endpoint
    try:
        response = requests.get(f"{API_BASE}/symbols")
        if response.status_code == 200:
            symbols = response.json()
            print(f"✅ Available symbols: {symbols}")
            
            if symbols:
                # Test price endpoint for first symbol
                symbol = symbols[0]
                response = requests.get(f"{API_BASE}/price/{symbol}")
                if response.status_code == 200:
                    price_data = response.json()
                    print(f"✅ Price data for {symbol}: ₹{price_data['price']}")
                else:
                    print(f"⚠️  No price data for {symbol} yet (expected if no market feed)")
                
                # Test OHLCV endpoint
                response = requests.get(f"{API_BASE}/ohlcv/{symbol}?minutes=10")
                if response.status_code == 200:
                    ohlcv_data = response.json()
                    print(f"✅ OHLCV data: {len(ohlcv_data)} records")
                else:
                    print(f"⚠️  No OHLCV data for {symbol} yet (expected if no market feed)")
            else:
                print("⚠️  No symbols available yet (expected if no market feed)")
            
            return True
        else:
            print(f"❌ Symbols endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market data test error: {e}")
        return False

def test_alerts(token):
    """Test alert endpoints"""
    print("Testing alert endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test creating an alert
    try:
        alert_data = {
            "symbol": "RELIANCE",
            "condition_type": ">",
            "target_price": 2500.00,
            "alert_type": "one_shot"
        }
        response = requests.post(f"{API_BASE}/alerts", json=alert_data, headers=headers)
        if response.status_code == 200:
            alert = response.json()
            print(f"✅ Alert created: ID {alert['id']}")
            alert_id = alert['id']
            
            # Test getting user alerts
            response = requests.get(f"{API_BASE}/alerts", headers=headers)
            if response.status_code == 200:
                alerts = response.json()
                print(f"✅ User alerts: {len(alerts)} alerts")
            
            # Test updating alert
            update_data = {"target_price": 2600.00}
            response = requests.put(f"{API_BASE}/alerts/{alert_id}", json=update_data, headers=headers)
            if response.status_code == 200:
                print("✅ Alert updated successfully")
            
            # Test getting alert triggers
            response = requests.get(f"{API_BASE}/alerts/{alert_id}/triggers", headers=headers)
            if response.status_code == 200:
                triggers = response.json()
                print(f"✅ Alert triggers: {len(triggers)} triggers")
            
            # Test deleting alert
            response = requests.delete(f"{API_BASE}/alerts/{alert_id}", headers=headers)
            if response.status_code == 200:
                print("✅ Alert deleted successfully")
            
            return True
        else:
            print(f"❌ Alert creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Alert test error: {e}")
        return False

def test_user_info(token):
    """Test user info endpoint"""
    print("Testing user info endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User info: {user_data['email']}")
            return True
        else:
            print(f"❌ User info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User info error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting QuantAlert System Tests")
    print("=" * 50)
    
    # Wait for services to start
    print("Waiting for services to start...")
    time.sleep(5)
    
    # Test health
    if not test_health():
        print("❌ System is not healthy. Please check if services are running.")
        return
    
    print()
    
    # Test registration
    if not test_registration():
        print("❌ Registration failed")
        return
    
    print()
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed")
        return
    
    print()
    
    # Test market data
    test_market_data(token)
    
    print()
    
    # Test alerts
    test_alerts(token)
    
    print()
    
    # Test user info
    test_user_info(token)
    
    print()
    print("=" * 50)
    print("✅ All tests completed!")
    print()
    print("Next steps:")
    print("1. Check MailHog at http://localhost:8025 for email testing")
    print("2. View API docs at http://localhost:8000/docs")
    print("3. Monitor logs with: docker-compose logs -f")
    print("4. Create alerts and watch for email notifications")

if __name__ == "__main__":
    main()
