from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .models import AlertRule, AlertTrigger
from .market_data import market_data
from .email_service import send_alert_email


class AlertEngine:
    def __init__(self):
        self.triggered_rules = set()  # Track recently triggered rules to avoid spam
    
    def evaluate_condition(self, current_price: Decimal, condition_type: str, target_price: Decimal) -> bool:
        """Evaluate if a price condition is met"""
        if condition_type == ">":
            return current_price > target_price
        elif condition_type == ">=":
            return current_price >= target_price
        elif condition_type == "<":
            return current_price < target_price
        elif condition_type == "<=":
            return current_price <= target_price
        elif condition_type == "==":
            return current_price == target_price
        else:
            return False
    
    def should_trigger_alert(self, alert_rule: AlertRule, db: Session) -> bool:
        """Check if an alert should be triggered based on cooldown and previous triggers"""
        # Check if rule is active
        if not alert_rule.is_active:
            return False
        
        # For one-shot alerts, check if already triggered
        if alert_rule.alert_type == "one_shot":
            existing_trigger = db.query(AlertTrigger).filter(
                AlertTrigger.alert_rule_id == alert_rule.id
            ).first()
            if existing_trigger:
                return False
        
        # For recurring alerts, check cooldown
        if alert_rule.alert_type == "recurring" and alert_rule.cooldown_minutes > 0:
            cooldown_time = datetime.now() - timedelta(minutes=alert_rule.cooldown_minutes)
            recent_trigger = db.query(AlertTrigger).filter(
                and_(
                    AlertTrigger.alert_rule_id == alert_rule.id,
                    AlertTrigger.triggered_at > cooldown_time
                )
            ).first()
            if recent_trigger:
                return False
        
        return True
    
    def get_value_for_rule(self, symbol: str, alert_rule: AlertRule) -> Optional[Decimal]:
        """Fetch the current value for the alert rule based on its data source and column"""
        try:
            if alert_rule.data_source == "tick":
                price_data = market_data.get_latest_price(symbol)
                if not price_data:
                    return None
                if alert_rule.column_name == "price":
                    return price_data.price
                if alert_rule.column_name == "volume":
                    return Decimal(price_data.volume)
                # Unsupported column for tick
                return None
            elif alert_rule.data_source == "ohlcv":
                ohlcvs = market_data.get_ohlcv_1min(symbol, alert_rule.ohlcv_timeframe_minutes)
                if not ohlcvs:
                    return None
                latest = ohlcvs[0]
                mapping = {
                    "open_price": latest.open_price,
                    "high_price": latest.high_price,
                    "low_price": latest.low_price,
                    "close_price": latest.close_price,
                    "volume": Decimal(latest.volume),
                }
                return mapping.get(alert_rule.column_name)
            else:
                return None
        except Exception:
            return None

    def process_symbol_alerts(self, symbol: str, current_price: Decimal, db: Session):
        """Process all alerts for a given symbol"""
        alert_rules = db.query(AlertRule).filter(
            and_(
                AlertRule.symbol == symbol,
                AlertRule.is_active == True
            )
        ).all()
        
        for alert_rule in alert_rules:
            value = self.get_value_for_rule(symbol, alert_rule)
            if value is None:
                continue
            if self.evaluate_condition(value, alert_rule.condition_type, alert_rule.target_price):
                if self.should_trigger_alert(alert_rule, db):
                    self.trigger_alert(alert_rule, value, db)
    
    def trigger_alert(self, alert_rule: AlertRule, triggered_price: Decimal, db: Session):
        """Trigger an alert and send email notification"""
        # Create trigger record
        trigger = AlertTrigger(
            alert_rule_id=alert_rule.id,
            triggered_price=triggered_price
        )
        db.add(trigger)
        db.commit()
        
        # Send email notification
        try:
            send_alert_email(
                to_email=alert_rule.user.email,
                symbol=alert_rule.symbol,
                condition_type=alert_rule.condition_type,
                target_price=alert_rule.target_price,
                triggered_price=triggered_price,
                alert_type=alert_rule.alert_type,
                data_source=alert_rule.data_source,
                column_name=alert_rule.column_name,
                ohlcv_timeframe_minutes=alert_rule.ohlcv_timeframe_minutes
            )
            
            # Mark email as sent
            trigger.email_sent = True
            trigger.email_sent_at = datetime.now()
            db.commit()
            
            print(f"Alert triggered for {alert_rule.symbol} at {triggered_price}")
            
        except Exception as e:
            print(f"Failed to send alert email: {e}")
    
    def process_all_alerts(self, db: Session):
        """Process alerts for all symbols with recent data"""
        symbols = market_data.get_all_symbols()
        
        for symbol in symbols:
            latest_price_data = market_data.get_latest_price(symbol)
            if latest_price_data:
                self.process_symbol_alerts(symbol, latest_price_data.price, db)


# Global instance
alert_engine = AlertEngine()
