from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertRuleBase(BaseModel):
    symbol: str
    condition_type: str  # >, >=, <, <=, ==
    target_price: Decimal
    alert_type: str = "one_shot"  # one_shot, recurring
    cooldown_minutes: int = 0


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    symbol: Optional[str] = None
    condition_type: Optional[str] = None
    target_price: Optional[Decimal] = None
    alert_type: Optional[str] = None
    cooldown_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class AlertRule(AlertRuleBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertTrigger(BaseModel):
    id: int
    alert_rule_id: int
    triggered_price: Decimal
    triggered_at: datetime
    email_sent: bool
    email_sent_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PriceData(BaseModel):
    symbol: str
    price: Decimal
    volume: int
    timestamp: datetime
    exchange: str


class OHLCVData(BaseModel):
    symbol: str
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    timestamp: datetime
    exchange: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
