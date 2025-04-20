from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import SessionLocal, Subscription

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/admin/users")
def get_admin_users(db: Session = Depends(get_db)):
    user_ids = db.query(Subscription.user_id).distinct().all()
    return {"users": [uid[0] for uid in user_ids]}

@router.get("/admin/subscriptions")
def get_admin_subscriptions(db: Session = Depends(get_db)):
    subs = db.query(Subscription).all()
    return {"subscriptions": [
        {"user_id": s.user_id, "city": s.city, "last_sent": s.last_sent.isoformat() if s.last_sent else None}
        for s in subs
    ]}

@router.get("/admin/stats")
def get_admin_stats(db: Session = Depends(get_db)):
    stats = db.query(Subscription.city, func.count(Subscription.user_id)).group_by(Subscription.city).all()
    return {"stats": [
        {"city": city, "count": count}
        for city, count in stats
    ]}
