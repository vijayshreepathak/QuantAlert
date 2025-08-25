#!/usr/bin/env python3
"""
Test script for QuantAlert Web Application
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health check passed")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_register():
    """Test user registration"""
    print("🔍 Testing user registration...")
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/register", json=data)
    if response.status_code == 200:
        print("✅ Registration successful")
        return True
    else:
        print(f"⚠️  Registration response: {response.status_code} - {response.text}")
        return False

def test_login():
    """Test user login"""
    print("🔍 Testing user login...")
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/token", data=data)
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login successful")
        return token_data["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_symbols(token):
    """Test symbols endpoint with authentication"""
    print("🔍 Testing symbols endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/symbols", headers=headers)
    if response.status_code == 200:
        symbols = response.json()
        print(f"✅ Symbols retrieved: {len(symbols)} symbols")
        return True
    else:
        print(f"❌ Symbols failed: {response.status_code} - {response.text}")
        return False

def test_create_alert(token):
    """Test alert creation"""
    print("🔍 Testing alert creation...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "symbol": "RELIANCE",
        "condition_type": ">",
        "target_price": 2500.0,
        "alert_type": "one_shot",
        "cooldown_minutes": 0
    }
    response = requests.post(f"{BASE_URL}/api/v1/alerts", json=data, headers=headers)
    if response.status_code == 200:
        print("✅ Alert created successfully")
        return True
    else:
        print(f"❌ Alert creation failed: {response.status_code} - {response.text}")
        return False

def test_get_alerts(token):
    """Test getting alerts"""
    print("🔍 Testing get alerts...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/alerts", headers=headers)
    if response.status_code == 200:
        alerts = response.json()
        print(f"✅ Alerts retrieved: {len(alerts)} alerts")
        return True
    else:
        print(f"❌ Get alerts failed: {response.status_code} - {response.text}")
        return False

def main():
    """Run all tests"""
    print("🚀 QuantAlert Web Application Test")
    print("=" * 40)
    
    # Test health
    if not test_health():
        print("❌ Health check failed, stopping tests")
        return
    
    # Test registration
    test_register()
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed, stopping tests")
        return
    
    # Test authenticated endpoints
    test_symbols(token)
    test_create_alert(token)
    test_get_alerts(token)
    
    print("\n✅ All tests completed!")
    print("\n🌐 Web Application is ready!")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("🔑 Login with: test@example.com / testpassword123")

if __name__ == "__main__":
    main()
