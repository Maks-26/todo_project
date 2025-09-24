# app/routes/admin.py

from fastapi import APIRouter, Depends

from app.dependencies import require_admin
from app.models import User

router = APIRouter()


@router.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_admin)):
    return {"message": f"Welcome, admin {current_user.email}!"}
