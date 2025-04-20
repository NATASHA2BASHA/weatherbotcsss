from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.database.models import SessionLocal, Subscription
import secrets

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBasic()

ADMIN_USER = "admin"
ADMIN_PASS = "s3cr3t"

def check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USER)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

@router.get("/stats", dependencies=[Depends(check_admin)])
def get_stats():
    with SessionLocal() as db:
        users = db.query(Subscription.user_id).distinct().count()
        subs  = db.query(Subscription.city).count()
    return {"users": users, "subscriptions": subs}

@router.get("/users", dependencies=[Depends(check_admin)])
def list_users():
    with SessionLocal() as db:
        ids = [uid for (uid,) in db.query(Subscription.user_id).distinct().all()]
    return {"user_ids": ids}
