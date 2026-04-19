# doctor_config.py

DOCTORS = {
    "dr-mukesh": {
        "id": "dr-mukesh",
        "name": "Dr Mukesh",
        "calendar_id": "6ae583b423add448601b7a0ec297739a82149b673723287d9aa76350636da6db@group.calendar.google.com",

        "working_days": [0, 1, 2, 3, 4],  # Mon–Fri
        "working_hours": {
            "start": "10:00",
            "end": "18:00",
        },
        "slot_duration_minutes": 30,
        "buffer_minutes": 10,
    },

    
    "dr-anita": {
        "id": "dr-anita",
        "name": "Dr Anita",
        "calendar_id": "96fc1577018a3e683f497057375d6ab0bacbadc36ea80c6bbd8b794e83e43edc@group.calendar.google.com",
        "working_days": [1, 2, 3, 4, 5],
        "working_hours": {
            "start": "09:00",
            "end": "17:00",
        },
        "slot_duration_minutes": 20,
        "buffer_minutes": 5,
    },
}

# Backward compatibility
DEFAULT_DOCTOR_ID = "dr-mukesh"

# For Phase 2 compatibility (temporary)
DOCTOR_CONFIG = DOCTORS[DEFAULT_DOCTOR_ID]

from db.repository import get_doctor_by_slug


def get_doctor(slug: str):
    """
    DB-first doctor fetch with config fallback.
    Always returns a normalized doctor dict.
    """

    # -----------------------
    # 1. Try DB first
    # -----------------------
    doctor = get_doctor_by_slug(slug)

    if doctor:
        return {
            "id": doctor.doctor_id,
            "slug": doctor.slug,
            "name": doctor.name,
            "calendar_id": doctor.calendar_id,
            "working_days": doctor.working_days,
            "working_hours": {
                "start": doctor.work_start_time.strftime("%H:%M"),
                "end": doctor.work_end_time.strftime("%H:%M"),
            },
            "slot_duration_minutes": doctor.avg_consult_minutes,
            "buffer_minutes": doctor.buffer_minutes,
        }

    # -----------------------
    # 2. Fallback to config
    # -----------------------
    if slug in DOCTORS:
        raise RuntimeError(
        f"Doctor '{slug}' not found in DB. Onboard doctor before use."
    )


    # -----------------------
    # 3. Final fallback
    # -----------------------
    return DOCTOR_CONFIG
