# db/models.py

from sqlalchemy import (
    Column, String, Boolean, Integer, Time, Date, Text,
    ForeignKey, TIMESTAMP, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime   
from .database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    clinic_email = Column(String, nullable=False)
    
    doctor_whatsapp_number = Column(String, nullable=True)
    clinic_phone_number = Column(String, nullable=True)
    notifications_enabled = Column(Boolean, default=False)

    calendar_id = Column(String, nullable=False)

    working_days = Column(Text, nullable=False)  # stored as CSV e.g. "0,1,2,3,4"
    work_start_time = Column(Time, nullable=False)
    work_end_time = Column(Time, nullable=False)

    avg_consult_minutes = Column(Integer, default=15)
    buffer_minutes = Column(Integer, default=5)

    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    appointments = relationship("Appointment", back_populates="doctor")


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    first_seen_at = Column(TIMESTAMP, server_default=func.now())
    last_seen_at = Column(TIMESTAMP, server_default=func.now())

    appointments = relationship("Appointment", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.doctor_id"))
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id"))

    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)

    status = Column(String, default="BOOKED")
    calendar_event_id = Column(String)

    # ── NEW: treatment tracking (nullable — safe for existing rows) ──
    treatment_key    = Column(String(64), nullable=True)
    duration_minutes = Column(Integer,   nullable=True)
    # ────────────────────────────────────────────────────────────────

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")


class DoctorCalendarCredential(Base):
    __tablename__ = "doctor_calendar_credentials"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.doctor_id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    provider = Column(String, nullable=False)  # e.g. "google"

    calendar_id = Column(String, nullable=False)

    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)

    expires_at = Column(TIMESTAMP, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    doctor = relationship("Doctor", backref="calendar_credentials")


class DoctorAuth(Base):
    __tablename__ = "doctor_auth"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.doctor_id"),
        nullable=False,
        unique=True
    )

    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)


class PatientDoctorLink(Base):
    __tablename__ = "patient_doctor_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    phone_number = Column(String, nullable=False, unique=True)

    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.doctor_id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(TIMESTAMP, server_default=func.now())

    doctor = relationship("Doctor")