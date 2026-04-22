# channels/web.py

from typing import Dict
from agent import run_agent
from state import BookingState
from fastapi import HTTPException

# session_id -> BookingState
state_store: Dict[str, BookingState] = {}


def init_session(
    *,
    session_id: str,
    doctor_id: str,
    doctor_name: str
) -> None:
    """
    Initialize or reset a booking session for web flow.
    Behavior must match existing main.py exactly.
    """
    if session_id not in state_store:
        state_store[session_id] = BookingState()

    state = state_store[session_id]
    state.reset_flow()
    state.doctor_id = doctor_id
    state.doctor_name = doctor_name
    state.greeted = False


def handle_web_message(
    *,
    session_id: str,
    user_message: str
) -> str:
    """
    Handle a single web chat message.
    Pure logic — no FastAPI, no cookies, no responses.
    """
    if session_id not in state_store:
        raise HTTPException(
            status_code=400,
            detail="Session missing. Please start booking from the doctor's page."
        )

    state = state_store[session_id]

    if not state.doctor_id:
        raise HTTPException(
            status_code=400,
            detail="Doctor context is missing. Please start booking via the doctor's booking link."
        )

    try:
        reply = run_agent(user_message, state)
    except Exception as e:
        print("AGENT ERROR:", e)
        state.reset_flow()
        reply = "⚠ Something went wrong on our side."


    return reply
