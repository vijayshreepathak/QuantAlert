from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    alert_rules = relationship("AlertRule", back_populates="user", cascade="all, delete-orphan")


class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(50), nullable=False, index=True)
    condition_type = Column(String(10), nullable=False)  # >, >=, <, <=, ==
    target_price = Column(Numeric(10, 2), nullable=False)
    alert_type = Column(String(20), nullable=False, default="one_shot")  # one_shot, recurring
    cooldown_minutes = Column(Integer, default=0)
    # New fields for OHLCV/column-based alerts
    data_source = Column(String(20), nullable=False, default="tick")  # tick or ohlcv
    column_name = Column(String(20), nullable=False, default="price")  # price, volume, open_price, high_price, low_price, close_price
    ohlcv_timeframe_minutes = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="alert_rules")
    triggers = relationship("AlertTrigger", back_populates="alert_rule", cascade="all, delete-orphan")


class AlertTrigger(Base):
    __tablename__ = "alert_triggers"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False)
    triggered_price = Column(Numeric(10, 2), nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True))
    
    alert_rule = relationship("AlertRule", back_populates="triggers")
