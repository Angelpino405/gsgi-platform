from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class LicenseType(str, enum.Enum):
    D = "D"
    G = "G"
    DG = "D+G"


class ShiftStatus(str, enum.Enum):
    scheduled = "scheduled"
    active = "active"
    completed = "completed"
    missed = "missed"
    cancelled = "cancelled"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(String(300))
    license_type = Column(Enum(LicenseType), nullable=False)
    license_number = Column(String(50))
    license_expiry = Column(String(20))
    hire_date = Column(String(20))
    pay_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    shifts = relationship("Shift", back_populates="employee")
    clock_events = relationship("ClockEvent", back_populates="employee")


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    client_name = Column(String(200), nullable=False)
    address = Column(String(300))
    city = Column(String(100))
    state = Column(String(50), default="FL")
    zip_code = Column(String(20))
    contact_name = Column(String(150))
    contact_phone = Column(String(20))
    contact_email = Column(String(200))
    post_orders = Column(Text)
    billing_rate = Column(Float, default=0.0)
    requires_armed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    shifts = relationship("Shift", back_populates="site")


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    date = Column(String(20), nullable=False)
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    status = Column(Enum(ShiftStatus), default=ShiftStatus.scheduled)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="shifts")
    site = relationship("Site", back_populates="shifts")
    clock_events = relationship("ClockEvent", back_populates="shift")


class ClockEvent(Base):
    __tablename__ = "clock_events"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    event_type = Column(String(10), nullable=False)  # "in" or "out"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    latitude = Column(Float)
    longitude = Column(Float)
    notes = Column(Text)

    employee = relationship("Employee", back_populates="clock_events")
    shift = relationship("Shift", back_populates="clock_events")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    report_type = Column(String(50), default="DAR")  # DAR, Incident, Patrol
    date = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee")
    site = relationship("Site")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(300), nullable=False)
    role = Column(String(20), default="manager")  # admin, manager, guard
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
