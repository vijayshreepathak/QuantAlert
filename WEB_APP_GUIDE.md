# 🌐 QuantAlert Web Application

## 🎯 **Complete Web Interface for Real-Time Market Alerts**

A beautiful, modern web application that provides real-time market data, price alerts, and email notifications - **all without requiring any demat accounts or API keys!**

## 🚀 **Quick Start**

### **1. Start the Application**
```bash
python start_web.py
```

### **2. Open Your Browser**
Navigate to: **http://localhost:8000**

### **3. Register & Login**
- Create a new account with your email
- Login to access the dashboard

## ✨ **Features**

### **🎨 Beautiful Modern Interface**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live price updates via WebSocket
- **Modern UI**: Gradient backgrounds, glass morphism effects
- **Interactive Elements**: Hover effects, animations, notifications

### **📊 Real-Time Market Data**
- **Live Price Updates**: Every 10 seconds
- **Multiple Symbols**: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK
- **Price Movement Indicators**: Green for up, red for down
- **Volume Information**: Real-time trading volume

### **🔔 Smart Alert System**
- **Multiple Conditions**: >, >=, <, <=, ==
- **Alert Types**: One-shot or recurring
- **Email Notifications**: Instant email alerts when conditions are met
- **Alert Management**: Create, edit, delete, view history

### **📧 Email Notifications**
- **Instant Alerts**: Get notified immediately when prices hit targets
- **Customizable**: Set your own email for notifications
- **SMTP Support**: Works with Gmail, Outlook, or any SMTP server

## 🛠️ **How It Works**

### **No API Keys Required!**
The application uses **mock data** that simulates real market movements:
- Realistic price fluctuations (±1% changes)
- Random volume data
- Continuous updates every 10 seconds
- No external dependencies or API keys needed

### **Real-Time Architecture**
1. **WebSocket Connection**: Browser connects to server for live updates
2. **Background Worker**: Processes market data and checks alerts
3. **Database Storage**: SQLite database for users, alerts, and triggers
4. **Email Service**: SMTP integration for notifications

## 📱 **User Interface**

### **Login/Register**
- Simple email/password authentication
- Automatic session management
- Secure JWT tokens

### **Dashboard**
- **Live Market Data**: Real-time price cards for all symbols
- **Connection Status**: WebSocket connection indicator
- **User Profile**: Display user info and logout option

### **Create Alerts**
- **Symbol Selection**: Choose from available stocks
- **Condition Setup**: Select comparison operator and target price
- **Alert Type**: One-shot or recurring alerts
- **Email Configuration**: Set notification email

### **Manage Alerts**
- **Alert List**: View all your active alerts
- **Status Indicators**: Active vs triggered alerts
- **History**: View past trigger events
- **Delete Alerts**: Remove unwanted alerts

## 🔧 **Configuration**

### **Email Setup (Optional)**
To enable email notifications, update your `.env` file:

```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=alerts@quantalert.com
```

### **Gmail App Password Setup**
1. Go to Google Account settings
2. Enable 2-factor authentication
3. Generate an app password
4. Use the app password in SMTP_PASSWORD

## 🎯 **Use Cases**

### **Day Trading**
- Set alerts for entry/exit points
- Get notified of price breakouts
- Monitor multiple stocks simultaneously

### **Long-term Investing**
- Set alerts for target buy/sell prices
- Monitor portfolio positions
- Get notified of significant price movements

### **Learning & Testing**
- Practice trading strategies
- Test alert systems
- Learn market dynamics

## 🔒 **Security Features**

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password encryption
- **CORS Protection**: Cross-origin request security
- **Input Validation**: Server-side data validation

## 📊 **Technical Stack**

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLite (local development)
- **Real-time**: WebSocket connections
- **Styling**: Modern CSS with gradients and animations
- **Icons**: Font Awesome
- **Fonts**: Inter (Google Fonts)

## 🚀 **Deployment**

### **Local Development**
```bash
python start_web.py
```

### **Production Deployment**
1. Set up a production database (PostgreSQL)
2. Configure environment variables
3. Use a production ASGI server (Gunicorn)
4. Set up reverse proxy (Nginx)
5. Configure SSL certificates

## 🎨 **Customization**

### **Adding New Symbols**
Edit `app/simple_feed.py`:
```python
self.symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "NEW_SYMBOL"]
self.base_prices = {
    # ... existing prices ...
    "NEW_SYMBOL": Decimal("1000.00")
}
```

### **Changing Update Frequency**
Edit the sleep duration in `app/simple_feed.py`:
```python
await asyncio.sleep(10)  # Change to desired seconds
```

### **Customizing Styles**
Edit the CSS in `app/static/index.html` to match your brand colors and styling.

## 🐛 **Troubleshooting**

### **Application Won't Start**
1. Check if port 8000 is available
2. Ensure all dependencies are installed
3. Verify `.env` file exists

### **WebSocket Connection Issues**
1. Check browser console for errors
2. Verify firewall settings
3. Ensure no proxy interference

### **Email Not Working**
1. Verify SMTP settings in `.env`
2. Check Gmail app password setup
3. Test SMTP connection manually

## 📈 **Future Enhancements**

- **Real Market Data**: Integration with Yahoo Finance or Alpha Vantage
- **Charts & Graphs**: Interactive price charts
- **Portfolio Tracking**: Track multiple positions
- **Mobile App**: Native mobile application
- **Advanced Alerts**: Technical indicators, volume alerts
- **Social Features**: Share alerts, follow other traders

## 🎉 **Get Started Now!**

1. **Start the application**: `python start_web.py`
2. **Open browser**: http://localhost:8000
3. **Register account**: Use any email
4. **Create alerts**: Set your first price alert
5. **Watch it work**: See real-time updates and notifications

**No demat accounts, no API keys, no complex setup - just pure trading alert functionality!** 🚀
