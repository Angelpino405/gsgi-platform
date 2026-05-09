from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from database import get_db
from auth import get_current_user
import models

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    today = date.today().isoformat()
    week_end = (date.today() + timedelta(days=7)).isoformat()

    total_employees = db.query(models.Employee).filter(models.Employee.is_active == True).count()
    total_sites = db.query(models.Site).filter(models.Site.is_active == True).count()

    today_shifts = db.query(models.Shift).filter(models.Shift.date == today).all()
    today_covered = sum(1 for s in today_shifts if s.employee_id is not None)
    today_open = sum(1 for s in today_shifts if s.employee_id is None)

    active_shifts = db.query(models.Shift).filter(
        models.Shift.status == models.ShiftStatus.active
    ).count()

    week_shifts = db.query(models.Shift).filter(
        models.Shift.date >= today,
        models.Shift.date <= week_end,
        models.Shift.employee_id == None,
        models.Shift.status == models.ShiftStatus.scheduled
    ).count()

    recent_shifts = db.query(models.Shift).filter(
        models.Shift.date >= today
    ).order_by(models.Shift.date, models.Shift.start_time).limit(10).all()

    upcoming = []
    for s in recent_shifts:
        upcoming.append({
            "id": s.id,
            "date": s.date,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "site": s.site.name if s.site else "—",
            "employee": f"{s.employee.first_name} {s.employee.last_name}" if s.employee else "OPEN",
            "status": s.status,
        })

    return {
        "total_employees": total_employees,
        "total_sites": total_sites,
        "today_shifts_total": len(today_shifts),
        "today_shifts_covered": today_covered,
        "today_shifts_open": today_open,
        "active_shifts_now": active_shifts,
        "open_shifts_next_7_days": week_shifts,
        "upcoming_shifts": upcoming,
    }
