# auth_store.py

# Phase 7.2 – OAuth store (doctor-aware, in-memory)
oauth_store = {
    # doctor_id (UUID as str) -> google credentials
    "credentials": {},

    # OAuth flow (temporary, during connect)
    "flow": None,

    # doctor_id currently connecting calendar
    "pending_doctor": None,
}
