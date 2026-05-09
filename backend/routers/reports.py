from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Literal
from database import get_db
from auth import get_current_user
import models

router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportCreate(BaseModel):
    employee_id: int
    site_id: int
    shift_id: Optional[int] = None
    report_type: Literal["DAR", "Incident", "Patrol"] = "DAR"
    date: str
    content: str


def report_to_dict(r):
    return {
        "id": r.id,
        "employee_id": r.employee_id,
        "employee_name": f"{r.employee.first_name} {r.employee.last_name}" if r.employee else None,
        "site_id": r.site_id,
        "site_name": r.site.name if r.site else None,
        "shift_id": r.shift_id,
        "report_type": r.report_type,
        "date": r.date,
        "content": r.content,
        "created_at": str(r.created_at),
    }


@router.get("")
def list_reports(
    employee_id: Optional[int] = None,
    site_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    report_type: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(models.Report)
    if employee_id is not None:
        q = q.filter(models.Report.employee_id == employee_id)
    if site_id is not None:
        q = q.filter(models.Report.site_id == site_id)
    if date_from:
        q = q.filter(models.Report.date >= date_from)
    if date_to:
        q = q.filter(models.Report.date <= date_to)
    if report_type:
        q = q.filter(models.Report.report_type == report_type)
    return [report_to_dict(r) for r in q.order_by(models.Report.date.desc()).all()]


@router.post("")
def create_report(data: ReportCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    emp = db.query(models.Employee).filter(models.Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    site = db.query(models.Site).filter(models.Site.id == data.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    report = models.Report(**data.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report_to_dict(report)


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report_to_dict(report)
