# app/worker.py
from __future__ import annotations

import asyncio
from decimal import Decimal
from datetime import datetime, timezone

import aiohttp
from sqlalchemy.orm import Session

from .database import SessionLocal
from .market_feed import start_market_feeds
from .config import settings


class AlertWorker:
    """AlertWorker with WORKING alert processing and email sending"""
    
    def __init__(self):
        self.is_running = False

    def _new_db_session(self) -> Session:
        """Create fresh DB session"""
        return SessionLocal()

    async def _broadcast_price_update(self, message: dict):
        """Broadcast to WebSocket clients"""
        try:
            timeout = aiohttp.ClientTimeout(total=3)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post("http://127.0.0.1:8000/_internal/broadcast", 
                                       json=message) as response:
                    if response.status == 200:
                        print(f"📡 Broadcasted {message['symbol']} to WebSocket clients")
        except Exception as e:
            print(f"WebSocket broadcast error: {e}")

    async def price_update_callback(self, symbol: str, price, volume, exchange="NSE"):
        """Handle price updates AND process alerts - THIS IS THE KEY!"""
        try:
            price_decimal = Decimal(str(price))
            volume_int = int(volume or 0)
            
            print(f"📈 Price update: {symbol} = ₹{price_decimal}")
            
            # 1) Store market data
            try:
                from .market_data import market_data
                market_data.store_tick(symbol, price_decimal, volume_int, exchange)
                market_data.update_ohlcv_1min(symbol, price_decimal, volume_int, exchange)
            except Exception as e:
                print(f"❌ Market data storage error: {e}")

            # 2) Broadcast to WebSocket (for live UI updates)
            await self._broadcast_price_update({
                "type": "price_update",
                "symbol": symbol,
                "price": float(price_decimal),
                "volume": volume_int,
                "exchange": exchange,
                "timestamp": datetime.now().isoformat()
            })

            # 3) PROCESS ALERTS - This was completely missing!
            await self._process_alerts_for_symbol(symbol, price_decimal)

        except Exception as e:
            print(f"❌ Price callback error: {e}")

    async def _process_alerts_for_symbol(self, symbol: str, current_price: Decimal):
        """Process all alerts for a symbol - MAIN ALERT LOGIC"""
        db = self._new_db_session()
        try:
            from .models import AlertRule, AlertTrigger, User
            
            # Get all active alerts for this symbol
            alerts = db.query(AlertRule).join(User).filter(
                AlertRule.symbol == symbol,
                AlertRule.is_active == True
            ).all()
            
            if len(alerts) == 0:
                return
                
            print(f"🔍 Checking {len(alerts)} alerts for {symbol} at ₹{current_price}")
            
            for alert in alerts:
                try:
                    # Check if alert condition is met
                    should_trigger = self._check_alert_condition(alert, current_price)
                    
                    if should_trigger:
                        print(f"🚨 ALERT TRIGGERED: {alert.symbol} {alert.condition_type} ₹{alert.target_price}")
                        print(f"   Current price: ₹{current_price}")
                        print(f"   Sending email to: {alert.user.email}")
                        
                        # Send email and create trigger record
                        await self._send_alert_email(alert, current_price, db)
                        
                        # Disable one-shot alerts after triggering
                        if alert.alert_type == "one_shot":
                            alert.is_active = False
                            db.commit()
                            print(f"   🔄 One-shot alert disabled")
                            
                except Exception as e:
                    print(f"❌ Error processing alert {alert.id}: {e}")
                    db.rollback()
                    
        except Exception as e:
            print(f"❌ Error in alert processing: {e}")
        finally:
            db.close()

    def _check_alert_condition(self, alert, current_price: Decimal) -> bool:
        """Check if alert condition is triggered"""
        target = alert.target_price
        condition = alert.condition_type
        
        if condition == ">" and current_price > target:
            return True
        elif condition == ">=" and current_price >= target:
            return True
        elif condition == "<" and current_price < target:
            return True
        elif condition == "<=" and current_price <= target:
            return True
        elif condition == "==" and abs(current_price - target) < Decimal("0.01"):
            return True
        
        return False

    async def _send_alert_email(self, alert, triggered_price: Decimal, db: Session):
        """Send alert email with full error handling"""
        try:
            from .email_service import send_alert_email
            from .models import AlertTrigger
            
            print(f"📧 SENDING ALERT EMAIL to {alert.user.email}...")
            
            # Create trigger record first
            trigger = AlertTrigger(
                alert_rule_id=alert.id,
                triggered_price=triggered_price,
                triggered_at=datetime.now(timezone.utc),
                email_sent=False
            )
            db.add(trigger)
            db.flush()  # Get trigger ID
            
            # Send the email
            send_alert_email(
                to_email=alert.user.email,
                symbol=alert.symbol,
                condition_type=alert.condition_type,
                target_price=alert.target_price,
                triggered_price=triggered_price,
                alert_type=alert.alert_type,
                data_source=alert.data_source or "tick",
                column_name=alert.column_name or "price",
                ohlcv_timeframe_minutes=alert.ohlcv_timeframe_minutes or 1
            )
            
            # Mark as sent
            trigger.email_sent = True
            trigger.email_sent_at = datetime.now(timezone.utc)
            db.commit()
            
            print(f"✅ ALERT EMAIL SENT SUCCESSFULLY!")
            print(f"   To: {alert.user.email}")
            print(f"   Alert: {alert.symbol} {alert.condition_type} ₹{alert.target_price}")
            print(f"   Triggered at: ₹{triggered_price}")
            
        except Exception as e:
            print(f"❌ EMAIL SEND FAILED: {e}")
            print(f"   Alert ID: {alert.id}, User: {alert.user.email}")
            
            # Still commit trigger record even if email fails
            try:
                db.commit()
            except:
                db.rollback()

    async def start_market_feed(self):
        """Start market data feed"""
        print("🚀 Starting market data feed with alert processing...")
        try:
            await start_market_feeds(self.price_update_callback)
        except Exception as e:
            print(f"❌ Market feed startup failed: {e}")
            raise

    async def start(self):
        """Start the AlertWorker"""
        self.is_running = True
        print("🎯 Starting AlertWorker with FULL ALERT PROCESSING + EMAIL SENDING")
        
        try:
            await self.start_market_feed()
        except Exception as e:
            print(f"❌ AlertWorker error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the worker"""
        print("🛑 Stopping AlertWorker...")
        self.is_running = False


# Global worker instance
worker = AlertWorker()

async def main():
    """Main entry point"""
    try:
        await worker.start()
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal...")
    except Exception as e:
        print(f"❌ Worker error: {e}")
    finally:
        worker.stop()
        print("✅ AlertWorker stopped")

if __name__ == "__main__":
    asyncio.run(main())
