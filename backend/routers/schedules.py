from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from auth import get_current_user
import models

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


class ShiftCreate(BaseModel):
    site_id: int
    employee_id: Optional[int] = None
    date: str
    start_time: str
    end_time: str
    notes: Optional[str] = None


class ShiftUpdate(BaseModel):
    employee_id: Optional[int] = None
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: Optional[models.ShiftStatus] = None
    notes: Optional[str] = None


def shift_to_dict(s):
    return {
        "id": s.id,
        "site_id": s.site_id,
        "site_name": s.site.name if s.site else None,
        "client_name": s.site.client_name if s.site else None,
        "employee_id": s.employee_id,
        "employee_name": f"{s.employee.first_name} {s.employee.last_name}" if s.employee else "OPEN",
        "date": s.date,
        "start_time": s.start_time,
        "end_time": s.end_time,
        "status": s.status,
        "notes": s.notes,
        "created_at": str(s.created_at),
    }


@router.get("")
def list_shifts(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    employee_id: Optional[int] = None,
    site_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    q = db.query(models.Shift)
    if date_from:
        q = q.filter(models.Shift.date >= date_from)
    if date_to:
        q = q.filter(models.Shift.date <= date_to)
    if employee_id:
        q = q.filter(models.Shift.employee_id == employee_id)
    if site_id:
        q = q.filter(models.Shift.site_id == site_id)
    shifts = q.order_by(models.Shift.date, models.Shift.start_time).all()
    return [shift_to_dict(s) for s in shifts]


@router.get("/open")
def list_open_shifts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    shifts = db.query(models.Shift).filter(
        models.Shift.employee_id == None,
        models.Shift.status == models.ShiftStatus.scheduled
    ).order_by(models.Shift.date).all()
    return [shift_to_dict(s) for s in shifts]


@router.post("")
def create_shift(data: ShiftCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    site = db.query(models.Site).filter(models.Site.id == data.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    if data.employee_id:
        emp = db.query(models.Employee).filter(models.Employee.id == data.employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
    shift = models.Shift(**data.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift_to_dict(shift)


@router.put("/{shift_id}")
def update_shift(shift_id: int, data: ShiftUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    shift = db.query(models.Shift).filter(models.Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(shift, field, value)
    db.commit()
    db.refresh(shift)
    return shift_to_dict(shift)


@router.delete("/{shift_id}")
def cancel_shift(shift_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    shift = db.query(models.Shift).filter(models.Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    shift.status = models.ShiftStatus.cancelled
    db.commit()
    return {"message": "Shift cancelled"}


class ClockIn(BaseModel):
    employee_id: int
    shift_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


@router.post("/clock/in")
def clock_in(data: ClockIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    event = models.ClockEvent(
        employee_id=data.employee_id,
        shift_id=data.shift_id,
        event_type="in",
        latitude=data.latitude,
        longitude=data.longitude,
        notes=data.notes,
    )
    db.add(event)
    if data.shift_id:
        shift = db.query(models.Shift).filter(models.Shift.id == data.shift_id).first()
        if shift:
            shift.status = models.ShiftStatus.active
    db.commit()
    db.refresh(event)
    return {"id": event.id, "event_type": "in", "timestamp": str(event.timestamp)}


@router.post("/clock/out")
def clock_out(data: ClockIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    event = models.ClockEvent(
        employee_id=data.employee_id,
        shift_id=data.shift_id,
        event_type="out",
        latitude=data.latitude,
        longitude=data.longitude,
        notes=data.notes,
    )
    db.add(event)
    if data.shift_id:
        shift = db.query(models.Shift).filter(models.Shift.id == data.shift_id).first()
        if shift:
            shift.status = models.ShiftStatus.completed
    db.commit()
    db.refresh(event)
    return {"id": event.id, "event_type": "out", "timestamp": str(event.timestamp)}
