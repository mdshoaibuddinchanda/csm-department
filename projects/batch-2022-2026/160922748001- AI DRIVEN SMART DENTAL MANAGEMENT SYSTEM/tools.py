# tools.py

from datetime import datetime, timedelta
import pytz
import os

from calendar_oauth import build_calendar_service
from auth_store import oauth_store

# LEGACY (fallback only – do not add new logic here)
from doctor_config import DOCTORS, DEFAULT_DOCTOR_ID
from sqlalchemy import select
from db.database import SessionLocal
from db.models import DoctorCalendarCredential
from services.notification_service import notify_doctor_via_whatsapp

from db.repository import (
    create_patient,
    create_appointment,
    get_appointment_by_event_id,
    cancel_appointment_db,
    reschedule_appointment_db,
    get_doctor_by_id,
    get_appointment_by_id,
)

# Treatment catalogue — for duration and display name
from treatments import get_duration_for_treatment, get_treatment_by_key

TIMEZONE = "Asia/Kolkata"
DISABLE_CALENDAR = os.getenv("DISABLE_CALENDAR", "false").lower() == "true"


# ------------------------------------------------------------------
# Credential helpers
# ------------------------------------------------------------------

def get_credentials_for_doctor(doctor_id):
    """
    DB-first calendar credentials lookup.
    Falls back to in-memory store for safety.
    """
    from db.repository import get_doctor_calendar_credentials

    doctor_id_str = str(doctor_id)

    # 1️⃣ DB-first
    creds_row = get_doctor_calendar_credentials(doctor_id)
    if creds_row:
        from google.oauth2.credentials import Credentials

        return Credentials(
            token=creds_row.access_token,
            refresh_token=creds_row.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scopes=["https://www.googleapis.com/auth/calendar"],
            expiry=creds_row.expires_at,
        )

    # 2️⃣ Fallback to in-memory (temporary safety net)
    creds_map = oauth_store.get("credentials", {})
    return creds_map.get(doctor_id_str)


# ------------------------------------------------------------------
# LEGACY CONFIG-BASED DOCTOR FETCH (FALLBACK ONLY)
# ------------------------------------------------------------------
def _get_doctor(doctor_id: str):
    """
    ⚠️ LEGACY FALLBACK
    Do NOT add new logic dependencies on this.
    """
    return DOCTORS.get(doctor_id, DOCTORS[DEFAULT_DOCTOR_ID])


# ------------------------------------------------------------------
# DB-backed doctor fetch
# ------------------------------------------------------------------
def get_doctor_from_db(doctor_id):
    """
    DB-first doctor fetch.
    Returns None if not found or DB error.
    """
    db = None
    try:
        from db.database import SessionLocal
        from db.models import Doctor

        db = SessionLocal()
        return db.get(Doctor, doctor_id)
    except Exception:
        return None
    finally:
        if db:
            db.close()


# ------------------------------------------------------------------
# DB-first calendar identity
# ------------------------------------------------------------------
def get_calendar_id_for_doctor(doctor_id):
    with SessionLocal() as db:
        creds = db.execute(
            select(DoctorCalendarCredential).where(
                DoctorCalendarCredential.doctor_id == doctor_id
            )
        ).scalars().first()

        if not creds:
            raise RuntimeError("❌ No calendar credentials found for doctor")

        return creds.calendar_id or "primary"


# ------------------------------------------------------------------
# Availability check (DB-only)
# ------------------------------------------------------------------
def check_availability_db(
    date_str: str,
    time_str: str,
    doctor_id,
    exclude_appointment_id=None,
):
    """
    DB-only availability check.
    Returns True if slot is free, False if overlap exists.
    Never touches Google Calendar.
    """
    from db.database import SessionLocal
    from db.models import Appointment

    db = SessionLocal()
    try:
        q = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == datetime.strptime(date_str, "%Y-%m-%d").date(),
            Appointment.appointment_time == datetime.strptime(time_str, "%H:%M").time(),
            Appointment.status == "BOOKED",
        )

        if exclude_appointment_id:
            q = q.filter(Appointment.appointment_id != exclude_appointment_id)

        return not db.query(q.exists()).scalar()

    finally:
        db.close()


# ------------------------------------------------------------------
# Availability entry point (DB-first)
# ------------------------------------------------------------------
def check_availability(
    date_str: str,
    time_str: str,
    doctor_id: str,
    exclude_appointment_id=None,
) -> bool:
    try:
        return check_availability_db(
            date_str,
            time_str,
            doctor_id,
            exclude_appointment_id=exclude_appointment_id,
        )
    except Exception:
        # Fail closed: safer to block than double-book
        return False


# ------------------------------------------------------------------
# Booking — treatment-aware, backward compatible
# ------------------------------------------------------------------
def book_appointment(
    date_str: str,
    time_str: str,
    doctor_id,
    patient_name: str,
    patient_phone: str,
    treatment_key: str | None = None,   # optional — falls back gracefully
):
    """
    Books an appointment and creates a Google Calendar event.

    treatment_key (e.g. "root_canal") is optional.
    When provided:
      • Duration is taken from the treatment catalogue
      • Calendar event title and description include the treatment name
    When None:
      • Falls back to doctor.avg_consult_minutes (original behaviour)
    """
    if not doctor_id:
        raise ValueError("Doctor context missing during booking")

    db = SessionLocal()
    try:
        doctor_db = get_doctor_by_id(db, doctor_id)
        if not doctor_db:
            raise ValueError("Doctor not found during booking")

        # Always create a new patient record
        patient = create_patient(
            db,
            name=patient_name,
            phone=patient_phone
        )

        # Calendar creation is MANDATORY
        if DISABLE_CALENDAR:
            raise RuntimeError("Calendar integration is disabled")

        credentials = get_credentials_for_doctor(doctor_id)
        if not credentials:
            raise RuntimeError("Doctor calendar is not connected")

        service = build_calendar_service(credentials)
        tz = pytz.timezone(TIMEZONE)

        start_dt = tz.localize(
            datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        )

        # Treatment-aware duration
        if treatment_key:
            duration_minutes = get_duration_for_treatment(
                treatment_key,
                default_minutes=doctor_db.avg_consult_minutes or 30,
            )
            treatment = get_treatment_by_key(treatment_key)
            treatment_display = (
                treatment.display_name
                if treatment
                else treatment_key.replace("_", " ").title()
            )
        else:
            if not doctor_db.avg_consult_minutes:
                raise RuntimeError("Doctor consultation duration not configured")
            duration_minutes = doctor_db.avg_consult_minutes
            treatment_display = None

        end_dt = start_dt + timedelta(minutes=duration_minutes)

        calendar_id = get_calendar_id_for_doctor(doctor_id)

        # Build event title and description with treatment info when available
        if treatment_display:
            event_summary = f"Appointment – {patient_name} ({treatment_display})"
            event_description = (
                f"Patient Name: {patient_name}\n"
                f"Phone: {patient_phone}\n"
                f"Treatment: {treatment_display}\n"
                f"Duration: {duration_minutes} min\n\n"
                f"Booked via MedSchedule AI"
            )
        else:
            event_summary = f"New Appointment – {patient_name}"
            event_description = (
                f"Patient Name: {patient_name}\n"
                f"Phone: {patient_phone}\n\n"
                f"Booked via MedSchedule AI"
            )

        event = {
            "summary": event_summary,
            "description": event_description,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": TIMEZONE,
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": TIMEZONE,
            },
            "attendees": [
                {"email": doctor_db.email}
            ],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 30}
                ]
            }
        }

        created = service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates="all"
        ).execute()

        event_id = created["id"]

        appt = create_appointment(
            db,
            doctor_id=doctor_db.doctor_id,
            patient_id=patient.patient_id,
            appointment_date=datetime.strptime(date_str, "%Y-%m-%d").date(),
            appointment_time=datetime.strptime(time_str, "%H:%M").time(),
            status="BOOKED",
            calendar_event_id=event_id,
            treatment_key=treatment_key,
            duration_minutes=duration_minutes,
        )

        if not appt or not appt.calendar_event_id:
            # Rollback calendar event if DB write failed
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates="all"
            ).execute()
            raise RuntimeError("Appointment creation failed after calendar event creation")

        db.commit()

        # Doctor Notification (non-blocking)
        try:
            treatment_line = f"\nTreatment: {treatment_display}" if treatment_display else ""
            notify_doctor_via_whatsapp(
                doctor=appt.doctor,
                message=(
                    f"📅 New Appointment Booked\n\n"
                    f"Patient: {patient_name}\n"
                    f"Date: {date_str}\n"
                    f"Time: {time_str}{treatment_line}\n"
                    f"Duration: {duration_minutes} min\n"
                    f"Phone: {patient_phone}"
                )
            )
        except Exception:
            pass  # Never break booking flow

        return {
            "appointment_id": appt.appointment_id,
            "event_id": event_id,
            "date": date_str,
            "time": time_str,
            "treatment": treatment_display,
            "duration_minutes": duration_minutes,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ------------------------------------------------------------------
# Cancel
# ------------------------------------------------------------------
def cancel_appointment(event_id: str, doctor_id: str):
    appt = get_appointment_by_event_id(event_id)
    if not appt:
        return
    cancel_appointment_by_id(appt.appointment_id, doctor_id)


def cancel_appointment_by_id(appointment_id, doctor_id):
    appt = get_appointment_by_id(appointment_id)
    if not appt:
        return

    # 1️⃣ Delete from Google Calendar FIRST (if applicable)
    if not DISABLE_CALENDAR and appt.calendar_event_id:
        credentials = get_credentials_for_doctor(doctor_id)
        if not credentials:
            raise RuntimeError("Doctor calendar is not connected")

        calendar_id = get_calendar_id_for_doctor(doctor_id)
        service = build_calendar_service(credentials)

        try:
            service.events().delete(
                calendarId=calendar_id,
                eventId=appt.calendar_event_id,
                sendUpdates="all"
            ).execute()
        except Exception as e:
            raise RuntimeError(
                f"Failed to delete calendar event: {str(e)}"
            )

    # 2️⃣ ALWAYS cancel in DB
    cancel_appointment_db(appointment_id)


# ------------------------------------------------------------------
# Working day / clinic hours helpers
# ------------------------------------------------------------------

def is_working_day(date_str: str, doctor_id: str) -> bool:
    doctor = get_doctor_from_db(doctor_id)
    if not doctor:
        return False

    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    weekday = date_obj.weekday()  # 0=Mon

    working_days = list(map(int, doctor.working_days.split(",")))
    return weekday in working_days


def is_within_clinic_hours(time_str: str, doctor_id) -> bool:
    db = SessionLocal()
    try:
        doctor = get_doctor_by_id(db, doctor_id)
        if not doctor:
            return False

        requested_time = datetime.strptime(time_str, "%H:%M").time()
        return doctor.work_start_time <= requested_time <= doctor.work_end_time
    finally:
        db.close()


# ------------------------------------------------------------------
# Update calendar event (reschedule side-effect)
# ------------------------------------------------------------------
def update_calendar_event(
    *,
    doctor_id,
    event_id: str,
    new_date,
    new_time,
):
    """
    Update an existing Google Calendar event.
    Side-effect only. Must not affect DB logic.
    """
    if DISABLE_CALENDAR or not event_id:
        return

    credentials = get_credentials_for_doctor(doctor_id)
    if not credentials:
        return

    calendar_id = get_calendar_id_for_doctor(doctor_id)
    service = build_calendar_service(credentials)

    tz = pytz.timezone(TIMEZONE)
    start_dt = tz.localize(
        datetime.combine(
            datetime.strptime(new_date, "%Y-%m-%d").date(),
            datetime.strptime(new_time, "%H:%M").time(),
        )
    )

    doctor = get_doctor_from_db(doctor_id)
    end_dt = start_dt + timedelta(minutes=doctor.avg_consult_minutes)

    event = service.events().get(
        calendarId=calendar_id,
        eventId=event_id
    ).execute()

    event["start"] = {
        "dateTime": start_dt.isoformat(),
        "timeZone": TIMEZONE,
    }
    event["end"] = {
        "dateTime": end_dt.isoformat(),
        "timeZone": TIMEZONE,
    }

    service.events().patch(
        calendarId=calendar_id,
        eventId=event_id,
        body=event,
        sendUpdates="all"
    ).execute()