from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from auth import get_current_user
import models

router = APIRouter(prefix="/api/employees", tags=["employees"])


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    license_type: models.LicenseType
    license_number: Optional[str] = None
    license_expiry: Optional[str] = None
    hire_date: Optional[str] = None
    pay_rate: Optional[float] = 0.0
    notes: Optional[str] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    license_type: Optional[models.LicenseType] = None
    license_number: Optional[str] = None
    license_expiry: Optional[str] = None
    hire_date: Optional[str] = None
    pay_rate: Optional[float] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


def employee_to_dict(e):
    return {
        "id": e.id,
        "first_name": e.first_name,
        "last_name": e.last_name,
        "full_name": f"{e.first_name} {e.last_name}",
        "email": e.email,
        "phone": e.phone,
        "address": e.address,
        "license_type": e.license_type,
        "license_number": e.license_number,
        "license_expiry": e.license_expiry,
        "hire_date": e.hire_date,
        "pay_rate": e.pay_rate,
        "is_active": e.is_active,
        "notes": e.notes,
        "created_at": str(e.created_at),
    }


@router.get("")
def list_employees(active_only: bool = True, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Employee)
    if active_only:
        q = q.filter(models.Employee.is_active == True)
    return [employee_to_dict(e) for e in q.order_by(models.Employee.last_name).all()]


@router.post("")
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    existing = db.query(models.Employee).filter(models.Employee.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    emp = models.Employee(**data.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return employee_to_dict(emp)


@router.get("/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee_to_dict(emp)


@router.put("/{employee_id}")
def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(emp, field, value)
    db.commit()
    db.refresh(emp)
    return employee_to_dict(emp)


@router.delete("/{employee_id}")
def deactivate_employee(employee_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.is_active = False
    db.commit()
    return {"message": "Employee deactivated"}
