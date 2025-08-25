# 🚀 Easy Setup Guide (No Demat Account Required!)

## 🎯 **Quick Start - No API Keys Needed!**

You can run QuantAlert **immediately** without any demat accounts or API keys!

## 📋 **Option 1: Yahoo Finance (EASIEST - No Setup Required)**

### ✅ **What You Get:**
- **Real market data** from Yahoo Finance
- **No API key required**
- **No account creation needed**
- **Works immediately**

### 🚀 **How to Use:**
1. **Just start the system** - no configuration needed!
2. Yahoo Finance will automatically be used
3. Get real-time prices for Indian stocks

```bash
# Start the system
python start_local.py
```

### 📊 **Supported Symbols:**
- RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK
- HINDUNILVR, ITC, SBIN, BHARTIARTL, KOTAKBANK

### ⚡ **Update Frequency:**
- Every 30 seconds (respects rate limits)
- Real market prices during trading hours

---

## 📋 **Option 2: Alpha Vantage (Free Tier)**

### ✅ **What You Get:**
- **Free tier available** (5 API calls per minute)
- **Real-time market data**
- **Simple registration**

### 🔑 **Setup Steps:**
1. **Sign up**: Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. **Get free API key** (no credit card required)
3. **Add to .env file**:
   ```env
   ALPHA_VANTAGE_API_KEY=your-free-api-key-here
   ```

### 🚀 **How to Use:**
```bash
# Start the system
python start_local.py
```

### ⚡ **Update Frequency:**
- Every 12 seconds per symbol (respects rate limits)
- 5 API calls per minute (free tier)

---

## 🎯 **Priority Order**

The system automatically tries feeds in this order:

1. **Angel Broking** (if configured)
2. **OpenAlgo** (if configured)
3. **Upstox** (if configured)
4. **Dhan** (if configured)
5. **Alpha Vantage** (if API key provided)
6. **Yahoo Finance** (automatic fallback)
7. **Mock Data** (final fallback)

## 🚀 **Quick Start Commands**

### **Option A: Yahoo Finance (No Setup)**
```bash
# 1. Start the system
python start_local.py

# 2. Test it
python test_local.py

# 3. View API docs
start http://localhost:8000/docs
```

### **Option B: Alpha Vantage (Free API Key)**
```bash
# 1. Get free API key from Alpha Vantage
# 2. Add to .env file
# 3. Start the system
python start_local.py
```

## ✅ **Verification**

### **Check if it's working:**
```bash
# Test the API
curl http://localhost:8000/health

# Check symbols
curl http://localhost:8000/api/v1/symbols

# Get price data
curl http://localhost:8000/api/v1/price/RELIANCE
```

### **Expected Output:**
- **Health**: `{"status": "healthy"}`
- **Symbols**: `["RELIANCE", "TCS", "INFY", ...]`
- **Price**: `{"symbol": "RELIANCE", "price": 2500.50}`

## 🎉 **What You Can Do**

### **1. Create Alerts**
```bash
# Register user
curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Login and get token
curl -X POST "http://localhost:8000/api/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com&password=password123"

# Create alert (use token from login)
curl -X POST "http://localhost:8000/api/v1/alerts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE", "condition_type": ">", "target_price": 2500, "alert_type": "one_shot"}'
```

### **2. Monitor Prices**
- View real-time price updates in the logs
- Check API endpoints for current prices
- Set up alerts for price movements

### **3. Test Alerts**
- Create alerts with realistic target prices
- Watch for alert triggers in the logs
- Test different alert types (one-shot, recurring)

## 🔧 **Troubleshooting**

### **No Market Data:**
- Check if market is open (9:15 AM - 3:30 PM IST)
- Verify internet connection
- Check logs for error messages

### **API Not Responding:**
- Ensure the system is running
- Check if port 8000 is available
- Restart the system if needed

### **No Symbols Available:**
- Wait a few minutes for initial data
- Check if market feed is connected
- Verify symbol names are correct

## 📈 **Next Steps**

1. **Test the system** with Yahoo Finance (no setup needed)
2. **Create some alerts** and watch them work
3. **Get Alpha Vantage API key** for better data
4. **Customize symbols** based on your needs
5. **Set up email notifications** for alerts

## 🎯 **Success Indicators**

You'll know it's working when you see:
- ✅ "Started Yahoo Finance feed" in logs
- ✅ Real price updates every 30 seconds
- ✅ API endpoints returning data
- ✅ Alerts being processed

## 🚀 **Ready to Go!**

**No demat account? No problem!** 

Just run `python start_local.py` and you'll have a fully functional QuantAlert system with real market data from Yahoo Finance!

---

**Need help?** Check the logs for detailed information about what's happening.
