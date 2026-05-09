from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from auth import get_current_user
import models

router = APIRouter(prefix="/api/sites", tags=["sites"])


class SiteCreate(BaseModel):
    name: str
    client_name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = "FL"
    zip_code: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    post_orders: Optional[str] = None
    billing_rate: Optional[float] = 0.0
    requires_armed: Optional[bool] = False
    notes: Optional[str] = None


class SiteUpdate(BaseModel):
    name: Optional[str] = None
    client_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    post_orders: Optional[str] = None
    billing_rate: Optional[float] = None
    requires_armed: Optional[bool] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


def site_to_dict(s):
    return {
        "id": s.id,
        "name": s.name,
        "client_name": s.client_name,
        "address": s.address,
        "city": s.city,
        "state": s.state,
        "zip_code": s.zip_code,
        "full_address": f"{s.address}, {s.city}, {s.state} {s.zip_code}" if s.address else "",
        "contact_name": s.contact_name,
        "contact_phone": s.contact_phone,
        "contact_email": s.contact_email,
        "post_orders": s.post_orders,
        "billing_rate": s.billing_rate,
        "requires_armed": s.requires_armed,
        "is_active": s.is_active,
        "notes": s.notes,
        "created_at": str(s.created_at),
    }


@router.get("")
def list_sites(active_only: bool = True, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Site)
    if active_only:
        q = q.filter(models.Site.is_active == True)
    return [site_to_dict(s) for s in q.order_by(models.Site.name).all()]


@router.post("")
def create_site(data: SiteCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    site = models.Site(**data.model_dump())
    db.add(site)
    db.commit()
    db.refresh(site)
    return site_to_dict(site)


@router.get("/{site_id}")
def get_site(site_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site_to_dict(site)


@router.put("/{site_id}")
def update_site(site_id: int, data: SiteUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(site, field, value)
    db.commit()
    db.refresh(site)
    return site_to_dict(site)


@router.delete("/{site_id}")
def deactivate_site(site_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    site.is_active = False
    db.commit()
    return {"message": "Site deactivated"}
