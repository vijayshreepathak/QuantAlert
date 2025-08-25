# Angel Broking API Setup Guide

## 🎯 **Overview**
Angel Broking provides direct market data access through their SmartAPI. This guide will help you set up Angel Broking integration with QuantAlert.

## 📋 **Prerequisites**
1. Angel Broking trading account
2. SmartAPI access enabled
3. API credentials

## 🔑 **Getting API Credentials**

### Step 1: Enable SmartAPI
1. Log in to your Angel Broking account
2. Go to **Settings** → **API Settings**
3. Enable **SmartAPI**
4. Generate API key

### Step 2: Get Required Credentials
You'll need these credentials:
- **API Key**: Generated from SmartAPI settings
- **Client ID**: Your Angel Broking client ID
- **Password**: Your trading account password
- **Feed Token**: Generated after authentication

## ⚙️ **Configuration**

### 1. Update .env File
Edit your `.env` file and add your Angel Broking credentials:

```env
# Angel Broking Configuration
ANGEL_API_KEY=your-api-key-here
ANGEL_CLIENT_ID=your-client-id-here
ANGEL_PASSWORD=your-password-here
ANGEL_FEED_TOKEN=your-feed-token-here
```

### 2. Example Configuration
```env
ANGEL_API_KEY=abc123def456
ANGEL_CLIENT_ID=L123456
ANGEL_PASSWORD=your-trading-password
ANGEL_FEED_TOKEN=xyz789
```

## 🚀 **Starting the System**

### Option 1: Using the startup script
```bash
python start_local.py
```

### Option 2: Manual startup
```bash
# Terminal 1: Start API
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start worker
python -m app.worker
```

## ✅ **Verification**

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

### 2. Test Market Data
```bash
curl http://localhost:8000/api/v1/symbols
```

### 3. View API Documentation
Visit: http://localhost:8000/docs

## 📊 **Supported Symbols**
The system supports these symbols by default:
- RELIANCE
- TCS
- HDFCBANK
- INFY
- ICICIBANK
- HINDUNILVR
- ITC
- SBIN
- BHARTIARTL
- KOTAKBANK

## 🔧 **Troubleshooting**

### Common Issues

#### 1. Authentication Failed
- Verify your API key, client ID, and password
- Ensure SmartAPI is enabled
- Check if your account is active

#### 2. WebSocket Connection Failed
- Check your internet connection
- Verify the WebSocket URL is accessible
- Ensure no firewall blocking the connection

#### 3. No Market Data
- Check if market is open (9:15 AM - 3:30 PM IST)
- Verify symbol subscriptions
- Check API rate limits

### Error Messages

#### "Missing Angel Broking credentials"
- Add all required credentials to `.env` file
- Restart the application

#### "Authentication failed"
- Double-check your credentials
- Ensure account is not blocked

#### "WebSocket connection error"
- Check network connectivity
- Try restarting the application

## 📞 **Support**

### Angel Broking Support
- **Phone**: 1800-222-990
- **Email**: smartapi@angelbroking.com
- **Website**: https://smartapi.angelbroking.com

### QuantAlert Support
- Check the main README.md for general support
- Review logs for detailed error messages

## 🔒 **Security Notes**

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Keep API keys secure** and don't share them
4. **Monitor API usage** to avoid rate limits

## 📈 **Next Steps**

1. **Create alerts** using the API
2. **Monitor price movements** in real-time
3. **Set up email notifications** for alerts
4. **Customize symbols** based on your needs

## 🎉 **Success!**

Once configured, you'll see:
- Real-time price updates from Angel Broking
- Automatic alert processing
- Email notifications when conditions are met
- Full API access for creating and managing alerts

Your QuantAlert system is now connected to live market data from Angel Broking! 🚀
