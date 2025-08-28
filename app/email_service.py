# app/email_service.py
from __future__ import annotations

import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decimal import Decimal
from jinja2 import Template
from datetime import datetime

from .config import settings


def test_email_connection() -> bool:
    """Test SMTP connection with current settings"""
    try:
        print("🔧 Testing SMTP connection...")
        print(f"📡 Server: {settings.smtp_host}:{settings.smtp_port}")
        print(f"👤 User: {settings.smtp_user}")
        
        if not all([settings.smtp_user, settings.smtp_password]):
            print("❌ Missing SMTP credentials")
            return False
            
        context = ssl.create_default_context()
        
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.ehlo()
            print("✅ Connected to SMTP server")
            
            server.starttls(context=context)
            print("✅ TLS encryption enabled")
            
            server.ehlo()
            
            server.login(settings.smtp_user, settings.smtp_password)
            print("✅ Authentication successful")
            
        print("✅ SMTP connection test PASSED!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Check your Gmail App Password")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def send_test_email(to_email: str):
    """Send a test email to verify configuration"""
    print(f"📧 Sending test email to {to_email}...")
    
    try:
        send_alert_email(
            to_email=to_email,
            symbol="TEST",
            condition_type=">", 
            target_price=Decimal("1000.00"),
            triggered_price=Decimal("1050.00"),
            alert_type="test"
        )
        print("✅ Test email sent successfully!")
        
    except Exception as e:
        print(f"❌ Test email failed: {e}")
        raise


def send_alert_email(
    to_email: str,
    symbol: str,
    condition_type: str,
    target_price: Decimal,
    triggered_price: Decimal,
    alert_type: str,
    data_source: str = "tick",
    column_name: str = "price", 
    ohlcv_timeframe_minutes: int = 1,
):
    """Send price alert email notification"""
    
    # Validate settings
    if not all([settings.smtp_user, settings.smtp_password, settings.smtp_from]):
        raise ValueError("SMTP settings not configured properly")
    
    # Email templates
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>QuantAlert - Price Alert</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .alert-icon { font-size: 48px; color: #e74c3c; margin-bottom: 10px; }
            .symbol { font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
            .condition { font-size: 18px; color: #7f8c8d; margin-bottom: 20px; }
            .price-info { background-color: #ecf0f1; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .price-row { display: flex; justify-content: space-between; margin-bottom: 10px; }
            .price-label { font-weight: bold; color: #34495e; }
            .price-value { color: #e74c3c; font-weight: bold; }
            .footer { text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="alert-icon">🚨</div>
                <div class="symbol">{{ symbol }}</div>
                <div class="condition">Price Alert Triggered</div>
            </div>
            
            <div class="price-info">
                <div class="price-row">
                    <span class="price-label">Condition:</span>
                    <span class="price-value">{{ condition_type }} ₹{{ target_price }}</span>
                </div>
                <div class="price-row">
                    <span class="price-label">Current Price:</span>
                    <span class="price-value">₹{{ triggered_price }}</span>
                </div>
                <div class="price-row">
                    <span class="price-label">Alert Type:</span>
                    <span class="price-value">{{ alert_type.title() }}</span>
                </div>
            </div>
            
            <p>Your price alert for <strong>{{ symbol }}</strong> has been triggered!</p>
            
            <div class="footer">
                <p>📊 QuantAlert - Smart Price Monitoring</p>
                <p>🕐 {{ timestamp }}</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_template = """
    🚨 PRICE ALERT - {{ symbol }}
    
    Your price alert has been triggered!
    
    Symbol: {{ symbol }}
    Condition: {{ condition_type }} ₹{{ target_price }}
    Current Price: ₹{{ triggered_price }}
    Alert Type: {{ alert_type }}
    
    📊 QuantAlert
    🕐 {{ timestamp }}
    """

    # Render templates  
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    
    html_content = Template(html_template).render(
        symbol=symbol,
        condition_type=condition_type,
        target_price=target_price,
        triggered_price=triggered_price,
        alert_type=alert_type,
        timestamp=timestamp
    )
    
    text_content = Template(text_template).render(
        symbol=symbol,
        condition_type=condition_type,
        target_price=target_price,
        triggered_price=triggered_price,
        alert_type=alert_type,
        timestamp=timestamp
    )

    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚨 Alert: {symbol} {condition_type} ₹{target_price}"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    
    msg.attach(MIMEText(text_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    # Send email
    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            
            server.send_message(msg)
        
        print(f"✅ Alert email sent to {to_email} for {symbol}")
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Email authentication failed: {e}")
        print("💡 Check Gmail App Password settings")
        raise
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        raise
