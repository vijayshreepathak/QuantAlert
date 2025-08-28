def trigger_alert(self, alert_rule: AlertRule, triggered_price: Decimal, db: Session) -> None:
    """Trigger an alert and send email notification"""
    print(f"🚨 TRIGGERING ALERT: {alert_rule.symbol} {alert_rule.condition_type} ₹{alert_rule.target_price}")
    print(f"📊 Current price: ₹{triggered_price}")
    
    # Create trigger record
    trigger = AlertTrigger(
        alert_rule_id=alert_rule.id,
        triggered_price=triggered_price,
        triggered_at=datetime.now(timezone.utc),
        email_sent=False,
    )
    
    try:
        db.add(trigger)
        db.flush()  # Get trigger ID
        print(f"✅ Alert trigger record created with ID: {trigger.id}")
    except Exception as e:
        print(f"❌ Failed to create trigger record: {e}")
        db.rollback()
        return
    
    # Send email notification
    try:
        from .email_service import send_alert_email
        
        print(f"📧 Sending email to: {alert_rule.user.email}")
        
        send_alert_email(
            to_email=alert_rule.user.email,
            symbol=alert_rule.symbol,
            condition_type=alert_rule.condition_type,
            target_price=alert_rule.target_price,
            triggered_price=triggered_price,
            alert_type=alert_rule.alert_type,
            data_source=alert_rule.data_source,
            column_name=alert_rule.column_name,
            ohlcv_timeframe_minutes=alert_rule.ohlcv_timeframe_minutes or 1
        )
        
        # Mark email as sent
        trigger.email_sent = True
        trigger.email_sent_at = datetime.now(timezone.utc)
        db.commit()
        
        print(f"🎉 ALERT EMAIL SENT successfully to {alert_rule.user.email}")
        
    except Exception as e:
        print(f"❌ FAILED TO SEND EMAIL: {e}")
        print(f"📧 Attempted to send to: {alert_rule.user.email}")
        # Still commit the trigger record even if email fails
        db.commit()
