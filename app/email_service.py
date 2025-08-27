import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decimal import Decimal
from jinja2 import Template
from .config import settings


def send_alert_email(
    to_email: str,
    symbol: str,
    condition_type: str,
    target_price: Decimal,
    triggered_price: Decimal,
    alert_type: str,
    data_source: str = "tick",
    column_name: str = "price",
    ohlcv_timeframe_minutes: int = 1
):
    """Send alert email notification"""
    
    # Email template
    template_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Price Alert - {{ symbol }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
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
                    <span class="price-label">Data Source:</span>
                    <span class="price-value">{{ data_source.upper() }}</span>
                </div>
                <div class="price-row">
                    <span class="price-label">Column:</span>
                    <span class="price-value">{{ column_name.replace('_', ' ').title() }}</span>
                </div>
                {% if data_source == "ohlcv" %}
                <div class="price-row">
                    <span class="price-label">Timeframe:</span>
                    <span class="price-value">{{ ohlcv_timeframe_minutes }} minutes</span>
                </div>
                {% endif %}
                <div class="price-row">
                    <span class="price-label">Condition:</span>
                    <span class="price-value">{{ condition_type }} {{ target_price }}</span>
                </div>
                <div class="price-row">
                    <span class="price-label">Current Value:</span>
                    <span class="price-value">₹{{ triggered_price }}</span>
                </div>
                <div class="price-row">
                    <span class="price-label">Alert Type:</span>
                    <span class="price-value">{{ alert_type.title() }}</span>
                </div>
            </div>
            
            <p>Your price alert for <strong>{{ symbol }}</strong> has been triggered. The current price of ₹{{ triggered_price }} has met your condition of {{ condition_type }} ₹{{ target_price }}.</p>
            
            <div class="footer">
                <p>This alert was sent by QuantAlert</p>
                <p>Time: {{ timestamp }}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    template_text = """
    PRICE ALERT - {{ symbol }}
    
    Your price alert has been triggered!
    
    Symbol: {{ symbol }}
    Data Source: {{ data_source.upper() }}
    Column: {{ column_name.replace('_', ' ').title() }}
    {% if data_source == "ohlcv" %}Timeframe: {{ ohlcv_timeframe_minutes }} minutes{% endif %}
    Condition: {{ condition_type }} {{ target_price }}
    Current Value: ₹{{ triggered_price }}
    Alert Type: {{ alert_type }}
    
    This alert was sent by QuantAlert at {{ timestamp }}
    """
    
    # Render templates
    html_template = Template(template_html)
    text_template = Template(template_text)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = html_template.render(
        symbol=symbol,
        condition_type=condition_type,
        target_price=target_price,
        triggered_price=triggered_price,
        alert_type=alert_type,
        data_source=data_source,
        column_name=column_name,
        ohlcv_timeframe_minutes=ohlcv_timeframe_minutes,
        timestamp=timestamp
    )
    
    text_content = text_template.render(
        symbol=symbol,
        condition_type=condition_type,
        target_price=target_price,
        triggered_price=triggered_price,
        alert_type=alert_type,
        data_source=data_source,
        column_name=column_name,
        ohlcv_timeframe_minutes=ohlcv_timeframe_minutes,
        timestamp=timestamp
    )
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Price Alert: {symbol} - {condition_type} ₹{target_price}"
    msg['From'] = settings.smtp_from
    msg['To'] = to_email
    
    # Attach parts
    text_part = MIMEText(text_content, 'plain')
    html_part = MIMEText(html_content, 'html')
    
    msg.attach(text_part)
    msg.attach(html_part)
    
    # Send email
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_user and settings.smtp_password:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        
        print(f"Alert email sent to {to_email} for {symbol}")
        # Optionally, you can return a success response or log the event
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise