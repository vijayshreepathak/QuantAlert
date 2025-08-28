# 🚀 QuantAlert - Real-Time Stock Price Alert System

<div align="center">







**🎯 Complete Stock Price Alert System with Real-Time Notifications**

*Monitor stock prices -  Set intelligent alerts -  Get instant email notifications*

[🚀 Quick Start](#-quick-start) -  [📊 Features](#-features) -  [🏗️ Architecture](#️-system-architecture) -  [📖 Documentation](#-api-documentation)

</div>

***

## 🌟 Overview

QuantAlert is a **production-ready stock price alert system** that combines real-time market data, intelligent price monitoring, and instant email notifications in a beautiful web interface.

### ✨ Key Highlights

- 🔴 **Real-Time Market Data** - Yahoo Finance, Angel One, Upstox, Dhan integrations
- 🎯 **Smart Alerts** - Price thresholds, volume alerts, technical indicators  
- 📧 **Instant Notifications** - Email alerts with customizable templates
- 🌐 **Modern Web UI** - Responsive design with live WebSocket updates
- 🔐 **Enterprise Security** - JWT authentication, bcrypt password hashing
- 📊 **Production Ready** - PostgreSQL, Docker, horizontal scaling
- 🚀 **Zero Setup** - Works with mock data out-of-the-box

***

## 🚀 Quick Start

### 1. **Start Database**
```bash
docker-compose up -d postgres
```

### 2. **Launch Application**
```bash
python start_web.py
```

### 3. **Open Browser**
Navigate to: **http://localhost:8000**

### 4. **Stop Services** (when done)
```bash
docker-compose down
```

🎉 **That's it!** QuantAlert is now running with mock data for instant testing.

***

## 📱 Screenshots & Live Demo

### 🎨 **Modern Web Interface**

*Beautiful and intuitive alert creation interface with real-time form validation*

### 📊 **Live Market Data Dashboard**
 
*Real-time market data updates with price movement indicators and volume information*

### 🚨 **Alert Processing System**

*Console output showing successful alert triggering and email dispatch when price conditions are met*

### 📧 **Email Notifications**

*Actual email notification received by user demonstrating the complete alert-to-email workflow*

***

## 📋 Prerequisites

### System Requirements
- **Python 3.9+**
- **Docker & Docker Compose**
- **PostgreSQL 12+** (for production)
- **Modern Web Browser**

### Install Dependencies
```bash
pip install -r requirements.txt
```

***

## ⚙️ Configuration

### 📧 Email Setup (.env)

Create a `.env` file in the project root:

```env
# ==========================================
# 📧 EMAIL CONFIGURATION (Gmail Example)
# ==========================================

# SMTP Server Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_FROM=your-email@gmail.com

# ==========================================
# 📧 GMAIL SETUP INSTRUCTIONS
# ==========================================
# 1. Enable 2-Factor Authentication in Gmail
# 2. Go to: Google Account → Security → App passwords
# 3. Generate new app password for "Mail"
# 4. Use the 16-character app password above
# 5. Never use your regular Gmail password!
# 
# Other SMTP Examples:
# ---------------------
# Outlook: smtp-mail.outlook.com:587
# Yahoo: smtp.mail.yahoo.com:587
# Custom: your-smtp-server.com:587

# ==========================================
# 🗄️ DATABASE CONFIGURATION
# ==========================================

# PostgreSQL (Production)
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/quantalert_db

# SQLite (Development) - Alternative
# DATABASE_URL=sqlite:///./quantalert.db

# DuckDB (Market Data Storage)
DUCKDB_PATH=./data/market_data.duckdb

# ==========================================
# 🔐 SECURITY SETTINGS
# ==========================================

# JWT Secret (Change in production!)
SECRET_KEY=your-super-secret-jwt-key-change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ==========================================
# 📊 MARKET DATA SOURCES
# ==========================================

# Default provider (yahoo/angel/upstox/dhan)
FEED_PROVIDER=yahoo

# Yahoo Finance (No API key required!)
# Automatically enabled - works out of the box

# Angel Broking API (Optional)
ANGEL_API_KEY=your-angel-api-key
ANGEL_CLIENT_ID=your-angel-client-id
ANGEL_PASSWORD=your-angel-password
ANGEL_FEED_TOKEN=your-angel-feed-token

# Upstox API (Optional)
UPSTOX_API_KEY=your-upstox-api-key
UPSTOX_ACCESS_TOKEN=your-upstox-access-token

# Dhan API (Optional)
DHAN_API_KEY=your-dhan-api-key
DHAN_ACCESS_TOKEN=your-dhan-access-token

# Alpha Vantage (Optional)
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key

# ==========================================
# 🔧 APPLICATION SETTINGS
# ==========================================

# Environment
ENVIRONMENT=development  # development/production
DEBUG=True
API_BASE_URL=http://127.0.0.1:8000

# Logging
LOG_LEVEL=INFO
```

### 🏗️ Database Setup (PostgreSQL)

1. **Install PostgreSQL** (if not using Docker)
2. **Create Database:**
   ```sql
   CREATE DATABASE quantalert_db;
   ```
3. **Update DATABASE_URL** in `.env`
4. **Tables are auto-created** on first run

***

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           🚀 QuantAlert System Architecture                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────────┐
│   🌐 Frontend   │    │  📊 Market Data  │    │        🔔 Alert Engine         │
│                 │    │     Sources      │    │                                 │
│ • HTML/CSS/JS   │    │                  │    │ • Price Monitoring             │
│ • WebSocket     │◄──►│ • Yahoo Finance  │────┤ • Condition Evaluation         │
│ • Responsive    │    │ • Angel One      │    │ • Email Triggers               │
│ • Real-time     │    │ • Upstox/Dhan    │    │ • Alert History                │
└─────────────────┘    │ • Mock Data      │    └─────────────────────────────────┘
         │              └──────────────────┘                     │
         │                        │                              │
         ▼                        ▼                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         🎯 FastAPI Application Server                          │
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ ┌──────────────┐ │
│  │   🔐 Auth API   │  │  📊 Alerts API  │  │ 📈 Market API  │ │ 🔌 WebSocket │ │
│  │                 │  │                 │  │                │ │              │ │
│  │ • JWT Tokens    │  │ • CRUD Alerts   │  │ • Live Prices  │ │ • Real-time  │ │
│  │ • User Mgmt     │  │ • Trigger Hist  │  │ • Symbols      │ │ • Broadcast  │ │
│  │ • Password Hash │  │ • Conditions    │  │ • Volume Data  │ │ • Connection │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
         │                        │                              │
         ▼                        ▼                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────────┐
│ 📧 SMTP Service │    │ 🗄️  PostgreSQL  │    │    ⚡ Background Worker        │
│                 │    │    Database     │    │                                 │
│ • Email Queue   │    │                 │    │ • Market Feed Processing       │
│ • Templates     │    │ • Users         │    │ • Alert Evaluation             │
│ • Delivery Log  │    │ • Alerts        │    │ • Email Dispatch               │
│ • SMTP Config   │    │ • Triggers      │    │ • Data Storage                 │
└─────────────────┘    │ • Audit Logs    │    │ • WebSocket Broadcasting       │
                       └─────────────────┘    └─────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                          🔄 Data Flow Diagram                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

Market Data → Worker → Database ┌─ Alert Engine ──→ Email Service ──→ 📧 User
     │            │              │       │                    │
     │            │              │       ▼                    │
     │            │              └─ WebSocket ────────────────┼──→ 🌐 Frontend
     │            │                                           │
     └────────────┼───────────────────────────────────────────┘
                  │
                  ▼
            📊 Market Data Storage (DuckDB)
```

### 🔄 Data Flow

1. **📊 Market Data** → Worker receives live price feeds
2. **🔍 Alert Processing** → Worker evaluates user alert conditions  
3. **📧 Email Dispatch** → SMTP service sends notifications
4. **🌐 Real-time Updates** → WebSocket broadcasts to frontend
5. **💾 Data Storage** → PostgreSQL stores users/alerts, DuckDB stores ticks

***

## 📊 Features

### 🎯 **Intelligent Price Alerts**
- **Condition Types**: `>`, `>=`, `<`, `<=`, `==`
- **Alert Types**: One-shot, Recurring with cooldowns
- **Data Sources**: Live ticks, OHLCV bars (1m, 5m, 15m, 1h, 1d)
- **Advanced Conditions**: Price, Volume, High, Low, Close

### 📧 **Smart Email Notifications**
- **Beautiful HTML Templates** with company branding
- **Instant Delivery** via SMTP (Gmail, Outlook, custom)
- **Delivery Tracking** with success/failure logs
- **Alert History** with trigger timestamps

### 🌐 **Modern Web Interface**
- **Responsive Design** - Works on desktop, tablet, mobile
- **Real-time Updates** via WebSocket connections
- **User Authentication** - Secure JWT-based login/register
- **Interactive Dashboard** - Live price cards with animations
- **Alert Management** - Create, edit, delete, view history

### 📊 **Market Data Integration**
- **Yahoo Finance** - Free, no API key required (default)
- **Angel One SmartAPI** - Real-time WebSocket feeds
- **Upstox** - Professional trading data
- **Dhan** - Retail broker integration  
- **Mock Data** - For testing and development

### 🔒 **Enterprise Security**
- **JWT Authentication** with secure token refresh
- **bcrypt Password Hashing** with salt rounds
- **CORS Protection** with configurable origins
- **Input Validation** and SQL injection prevention
- **Rate Limiting** and abuse protection

### 🚀 **Production Features**
- **Docker Deployment** with multi-container setup
- **PostgreSQL** for scalable data storage
- **Horizontal Scaling** with multiple worker processes
- **Health Monitoring** with /health endpoints
- **Comprehensive Logging** with structured formats
- **Environment Configuration** via .env files

***

## 📁 Project Structure

```
QuantAlert/
├── 📁 app/                     # Application core
│   ├── 🐍 main.py             # FastAPI application & WebSocket
│   ├── 🔌 api.py              # REST API endpoints
│   ├── 🗄️ models.py           # SQLAlchemy database models
│   ├── 🔐 auth.py             # JWT authentication & user management
│   ├── ⚡ worker.py            # Background alert processing worker
│   ├── 📊 market_feed.py      # Market data feed orchestrator
│   ├── 📧 email_service.py    # SMTP email service
│   ├── 🔧 config.py           # Configuration management
│   ├── 💾 database.py         # Database connection & session
│   └── 📁 static/             # Frontend assets
│       └── 🌐 index.html      # Single-page web application
├── 📁 Screenshots/             # Application screenshots
│   ├── 🖼️ pic1.jpg            # Create alert interface
│   ├── 🖼️ pic2.jpg            # Alert trigger console logs
│   ├── 🖼️ pic3.jpg            # Email notification received
│   └── 🖼️ pic4.jpg            # Live market data dashboard
├── 📁 feeds/                   # Market data feed modules (optional)
│   ├── 🟡 yahoo_feed.py       # Yahoo Finance integration
│   ├── 😇 angel_feed.py       # Angel One SmartAPI
│   ├── 📈 upstox_feed.py      # Upstox integration
│   └── 📊 dhan_feed.py        # Dhan integration
├── 🐳 docker-compose.yml      # Docker services configuration
├── 📄 requirements.txt        # Python dependencies
├── ⚙️ .env.example           # Environment variables template
├── 🚀 start_web.py           # Application launcher script
└── 📖 README.md              # This documentation
```

***

## 🔧 API Documentation

### 🔐 Authentication Endpoints

```http
POST /api/v1/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

```http
POST /api/v1/token
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=secure_password
```

### 🎯 Alert Management

```http
GET /api/v1/alerts
Authorization: Bearer <jwt_token>
```

```http
POST /api/v1/alerts
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "symbol": "TCS",
  "condition_type": ">",
  "target_price": 3200.00,
  "alert_type": "one_shot",
  "data_source": "tick"
}
```

```http
DELETE /api/v1/alerts/{alert_id}
Authorization: Bearer <jwt_token>
```

### 📊 Market Data

```http
GET /api/v1/symbols
```

```http
GET /api/v1/market-data/{symbol}
```

### 📈 Alert History

```http
GET /api/v1/alerts/{alert_id}/triggers
Authorization: Bearer <jwt_token>
```

### 🌐 WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'price_update') {
        console.log(`${data.symbol}: ₹${data.price}`);
    }
};
```

***

## 🚀 Deployment

### 🐳 Docker Production Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/vijayshreepathak/quantalert.git
   cd quantalert
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start All Services**
   ```bash
   docker-compose up -d
   ```

4. **Scale Workers** (optional)
   ```bash
   docker-compose up -d --scale worker=3
   ```

### 🔧 Manual Production Setup

1. **Install PostgreSQL & Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql redis-server
   
   # macOS
   brew install postgresql redis
   ```

2. **Create Database**
   ```sql
   CREATE DATABASE quantalert_db;
   CREATE USER quantalert WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE quantalert_db TO quantalert;
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run with Gunicorn**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

5. **Start Background Worker**
   ```bash
   python -m app.worker
   ```

### 🌐 Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

***

## 🛠️ Development

### 🔧 Local Development Setup

1. **Install Development Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run in Development Mode**
   ```bash
   python start_web.py --reload
   ```

3. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

4. **Code Formatting**
   ```bash
   black app/
   isort app/
   flake8 app/
   ```

### 🧪 Testing Email Configuration

```bash
# Test SMTP connection
python -c "
from app.email_service import test_email_connection
print('✅ Success' if test_email_connection() else '❌ Failed')
"

# Send test email
python -c "
from app.email_service import send_test_email
send_test_email('your-email@gmail.com')
"
```

***

## 🔍 Monitoring & Debugging

### 📊 Health Check Endpoints

```http
GET /health                    # Application health
GET /_internal/status         # Internal worker status
```

### 📈 Database Queries

```sql
-- Check recent alerts
SELECT u.email, a.symbol, a.target_price, a.created_at 
FROM alerts a 
JOIN users u ON a.user_id = u.id 
ORDER BY a.created_at DESC 
LIMIT 10;

-- Check triggered alerts
SELECT * FROM alert_triggers 
ORDER BY triggered_at DESC 
LIMIT 10;

-- Check email delivery status
SELECT t.*, a.symbol, u.email
FROM alert_triggers t
JOIN alerts a ON t.alert_rule_id = a.id
JOIN users u ON a.user_id = u.id
WHERE t.email_sent = false;
```

### 🔍 Log Analysis

```bash
# Follow application logs
docker-compose logs -f app

# Follow worker logs  
docker-compose logs -f worker

# Search for errors
docker-compose logs app | grep ERROR
```

***

## ❗ Troubleshooting

### 🔧 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 📧 **Emails not sending** | SMTP configuration | Check Gmail App Password, verify SMTP settings |
| 🔌 **WebSocket not connecting** | Firewall/Proxy | Check port 8000, disable firewall temporarily |
| 💾 **Database connection failed** | PostgreSQL not running | Start PostgreSQL service, check credentials |
| 📊 **No market data** | Feed provider issue | Check API keys, switch to mock data for testing |
| 🔐 **Login not working** | JWT secret | Regenerate SECRET_KEY in .env |

### 📧 Email Configuration Issues

**Gmail Setup:**
1. Enable 2-Factor Authentication
2. Generate App Password: Google Account → Security → App passwords
3. Use 16-character app password, not regular Gmail password
4. Set `SMTP_HOST=smtp.gmail.com` and `SMTP_PORT=587`

**Common SMTP Settings:**
```env
# Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Outlook
SMTP_HOST=smtp-mail.outlook.com  
SMTP_PORT=587

# Yahoo
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
```

### 🐛 Debug Mode

```bash
# Enable debug logging
export DEBUG=True
export LOG_LEVEL=DEBUG
python start_web.py
```

***

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### 🔄 Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes and add tests
4. **Commit** your changes: `git commit -m 'Add amazing feature'`
5. **Push** to the branch: `git push origin feature/amazing-feature`
6. **Open** a Pull Request

### 📝 Code Standards

- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **pytest** for testing
- **Type hints** for all functions
- **Docstrings** for all classes and functions

***

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

***

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Powerful, open source object-relational database
- **Yahoo Finance** - Free stock market data API
- **Font Awesome** - Beautiful icons for web interfaces
- **Docker** - Platform for developing, shipping, and running applications

***

## 📞 Support

### 🆘 Getting Help

- 📖 **Contact**: [vijayshree9646@gmail.com](mailto:vijayshree9646@gmail.com)
- 🐛 **Bug Reports**: Create an issue in the repository
- 💡 **Feature Requests**: Open a discussion or issue
- 📧 **Direct Support**: Email for urgent issues

### 📊 System Requirements

- **Minimum**: 2GB RAM, 1 CPU core, 10GB storage
- **Recommended**: 4GB RAM, 2 CPU cores, 50GB storage  
- **Production**: 8GB RAM, 4 CPU cores, 100GB+ storage

***

<div align="center">

**🚀 Built with ❤️ by Vijayshree Vaibhav for traders and investors worldwide :)**