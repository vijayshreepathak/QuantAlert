from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import List
from .database import get_db
from .models import User, AlertRule, AlertTrigger
from .schemas import (
    UserCreate, User as UserSchema, AlertRuleCreate, AlertRule as AlertRuleSchema,
    AlertRuleUpdate, AlertTrigger as AlertTriggerSchema, PriceData, OHLCVData, Token
)
from .auth import get_current_active_user, get_password_hash, verify_password, create_access_token
from .market_data import market_data
from datetime import timedelta
from .config import settings

router = APIRouter()


# Authentication endpoints
@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/token", response_model=Token)
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Login and get access token"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# Market data endpoints
@router.get("/price/{symbol}", response_model=PriceData)
def get_latest_price(symbol: str):
    """Get latest price for a symbol"""
    price_data = market_data.get_latest_price(symbol)
    if not price_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price data found for {symbol}"
        )
    return price_data


@router.get("/ohlcv/{symbol}", response_model=List[OHLCVData])
def get_ohlcv_data(symbol: str, minutes: int = 60):
    """Get OHLCV data for a symbol"""
    ohlcv_data = market_data.get_ohlcv_1min(symbol, minutes)
    if not ohlcv_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No OHLCV data found for {symbol}"
        )
    return ohlcv_data


@router.get("/symbols", response_model=List[str])
def get_all_symbols():
    """Get all available symbols"""
    return market_data.get_all_symbols()


# Alert endpoints
@router.post("/alerts", response_model=AlertRuleSchema)
def create_alert(
    alert: AlertRuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new alert rule"""
    db_alert = AlertRule(
        user_id=current_user.id,
        symbol=alert.symbol,
        condition_type=alert.condition_type,
        target_price=alert.target_price,
        alert_type=alert.alert_type,
        cooldown_minutes=alert.cooldown_minutes
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/alerts", response_model=List[AlertRuleSchema])
def get_user_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all alert rules for the current user"""
    alerts = db.query(AlertRule).filter(AlertRule.user_id == current_user.id).all()
    return alerts


@router.get("/alerts/{alert_id}", response_model=AlertRuleSchema)
def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific alert rule"""
    alert = db.query(AlertRule).filter(
        AlertRule.id == alert_id,
        AlertRule.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return alert


@router.put("/alerts/{alert_id}", response_model=AlertRuleSchema)
def update_alert(
    alert_id: int,
    alert_update: AlertRuleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an alert rule"""
    alert = db.query(AlertRule).filter(
        AlertRule.id == alert_id,
        AlertRule.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Update fields
    update_data = alert_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/alerts/{alert_id}")
def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an alert rule"""
    alert = db.query(AlertRule).filter(
        AlertRule.id == alert_id,
        AlertRule.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alert deleted successfully"}


@router.get("/alerts/{alert_id}/triggers", response_model=List[AlertTriggerSchema])
def get_alert_triggers(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trigger history for an alert rule"""
    # Verify alert belongs to user
    alert = db.query(AlertRule).filter(
        AlertRule.id == alert_id,
        AlertRule.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    triggers = db.query(AlertTrigger).filter(
        AlertTrigger.alert_rule_id == alert_id
    ).order_by(AlertTrigger.triggered_at.desc()).all()
    
    return triggers


# User endpoints
@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user
