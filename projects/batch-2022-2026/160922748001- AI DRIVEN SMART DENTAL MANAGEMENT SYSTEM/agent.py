# agent.py

import re
from datetime import datetime, timedelta

import pytz

from extractor import extract_entities
from state import BookingState
import state
from tools import check_availability, book_appointment, cancel_appointment, is_working_day
from state import FlowStage

from tools import cancel_appointment_by_id, update_calendar_event, is_within_clinic_hours
from uuid import UUID
from db.repository import reschedule_appointment_db
from db.database import SessionLocal

from db.repository import (
    get_patients_by_phone,
    get_active_appointments_by_phone,
    get_doctor_by_id
)

from treatments import (
    get_treatment_by_alias,
    get_treatment_by_key,
    list_treatments_for_display,
    TREATMENT_CATALOGUE,
)

import logging
logger = logging.getLogger("medschedule")


CONTROL_WORDS = {"yes", "no", "confirm", "ok", "okay"}

BOOK_KEYWORDS       = {"book", "appointment", "schedule"}
CANCEL_KEYWORDS     = {"cancel", "delete", "remove", "drop"}
RESCHEDULE_KEYWORDS = {"reschedule", "change", "move", "shift", "modify"}
RESET_KEYWORDS = {
    "start over", "restart", "reset",
    "sorry", "cancel this", "never mind", "forget it"
}


# ---------------------------
# Normalization helpers
# ---------------------------

def normalize_time(text: str):
    if not text:
        return None, False

    import re

    t = text.lower().strip()

    # --- Preprocessing ---
    t = t.replace(",", ":")
    t = t.replace(".", ":")

    # Convert formats like 1130 or 945 into 11:30 / 9:45
    if re.fullmatch(r"\d{3,4}", t):
        if len(t) == 3:   # e.g., 945 → 9:45
            t = f"{t[0]}:{t[1:]}"
        elif len(t) == 4: # e.g., 1130 → 11:30
            t = f"{t[:2]}:{t[2:]}"

    # Match HH or HH:MM with optional am/pm
    m = re.search(r"\b(\d{1,2})(?::(\d{1,2}))?\s*(am|pm)?\b", t)

    if not m:
        return None, True

    hour = int(m.group(1))
    minute = int(m.group(2)) if m.group(2) else 0
    meridiem = m.group(3)

    # Validate minute
    if minute < 0 or minute > 59:
        return None, True

    # --- Handle meridiem ---
    if meridiem == "pm" or "afternoon" in t or "evening" in t:
        if hour < 12:
            hour += 12

    elif meridiem == "am" or "morning" in t:
        if hour == 12:
            hour = 0

    else:
        # No AM/PM specified — assume 1–6 → PM, 7–11 → AM
        if 1 <= hour <= 6:
            hour += 12

    # Validate hour after adjustment
    if hour < 0 or hour > 23:
        return None, True

    return f"{hour:02d}:{minute:02d}", False


def normalize_date(text: str):
    if not text:
        return None

    t = text.lower()
    today = datetime.today()

    weekdays = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    for i, day in enumerate(weekdays):
        if day in t:
            days_ahead = (i - today.weekday() + 7) % 7
            if "next" in t and days_ahead == 0:
                days_ahead = 7
            target = today + timedelta(days=days_ahead)
            return target.strftime("%Y-%m-%d")

    if "today" in t:
        return today.strftime("%Y-%m-%d")

    if "tomorrow" in t:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    months = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]

    m1 = re.search(r"\b(\d{1,2})(st|nd|rd|th)?\b.*(" + "|".join(months) + r")", t)
    m2 = re.search(r"\b(" + "|".join(months) + r")\b.*(\d{1,2})(st|nd|rd|th)?", t)

    if m1:
        day = int(m1.group(1))
        month = months.index(m1.group(3)) + 1
    elif m2:
        day = int(m2.group(2))
        month = months.index(m2.group(1)) + 1
    else:
        return None

    year = today.year
    try:
        d = datetime(year, month, day)
        if d.date() < today.date():
            d = datetime(year + 1, month, day)
        return d.strftime("%Y-%m-%d")
    except:
        return None


# ---------------------------
# Main Agent
# ---------------------------

def run_agent(user_message: str, state: BookingState) -> str:

    # Phase 7.4.2 — hard safety guard
    if not state.doctor_id:
        return (
            "Doctor context is missing. "
            "Please start booking via the doctor's booking link."
        )

    # Phase 7.5 — doctor-aware greeting (once per session)
    if not state.greeted:
        state.greeted = True
        return (
            f"👋 Welcome to Dr. {state.doctor_name}'s clinic.\n"
            "I can help you book, cancel, or reschedule an appointment."
        )

    msg = user_message.strip().lower()

    # ---------------------------
    # 🔄 GLOBAL RESET (SAFE)
    # ---------------------------
    if any(k in msg for k in RESET_KEYWORDS):
        state.reset_flow()
        return "No problem 🙂 Let's start fresh. How can I help you?"

    doctor_id = state.doctor_id
    if not doctor_id:
        return "Sorry, doctor context is missing. Please refresh the page."

    # ---------------------------
    # 🔹 SELECTIVE LLM USE
    # ---------------------------
    use_llm = (
        state.intent is None
        or any(p in msg for p in [
            "after","around","same","earlier","later",
            "next","following","this","coming"
        ])
    )

    extracted = (
        extract_entities(user_message, state.intent)
        if use_llm
        else {
            "intent": None,
            "date_text": None,
            "time_text": None,
            "patient_name": None,
            "patient_phone": None,
            "treatment_text": None,
            "treatment_key": None,
            "confidence": "low",
        }
    )

    confidence = extracted.get("confidence", "low")

    # ---------------------------
    # 🔁 INTENT SWITCH GUARD
    # ---------------------------
    if state.intent and state.stage != FlowStage.IDLE:
        if any(w in msg for w in BOOK_KEYWORDS) and state.intent != "BOOK":
            return "You're in the middle of something. Do you want to start a new booking? (yes / no)"

        if any(w in msg for w in CANCEL_KEYWORDS) and state.intent != "CANCEL":
            return "You're in the middle of something. Do you want to cancel instead? (yes / no)"

        if any(w in msg for w in RESCHEDULE_KEYWORDS) and state.intent != "RESCHEDULE":
            return "You're in the middle of something. Do you want to reschedule instead? (yes / no)"

    if msg in CONTROL_WORDS and state.stage == FlowStage.IDLE:
        state.reset_flow()
        return "Alright. What would you like to do now?"

    # ---------------------------
    # INTENT DETECTION
    # ---------------------------
    if state.stage == FlowStage.IDLE:

        if confidence != "low" and extracted["intent"] and state.intent is None:
            state.intent = extracted["intent"]

        if state.intent is None:
            if any(w in msg for w in RESCHEDULE_KEYWORDS):
                state.intent = "RESCHEDULE"
            elif any(w in msg for w in CANCEL_KEYWORDS):
                state.intent = "CANCEL"
            elif any(w in msg for w in BOOK_KEYWORDS):
                state.intent = "BOOK"

        # Initialize flows once intent is known
        if state.intent == "BOOK":
            # Check if treatment was already mentioned in the first message
            treatment_key = extracted.get("treatment_key")
            if not treatment_key:
                treatment = get_treatment_by_alias(user_message)
                if treatment:
                    treatment_key = treatment.key

            if treatment_key:
                # Treatment already known — skip treatment step
                state.treatment_key = treatment_key
                state.stage = FlowStage.BOOK_DATE
            else:
                # Ask for treatment first
                state.stage = FlowStage.BOOK_TREATMENT
        elif state.intent == "RESCHEDULE":
            state.stage = FlowStage.RESCHEDULE_SELECT

    if state.intent is None:
        return "Hello 🙂 How can I help you today?"

    # ---------------------------
    # 🔁 CHANGE CHOICE (GLOBAL)
    # ---------------------------
    if state.stage == FlowStage.CHANGE_CHOICE:

        # Change DATE
        if msg == "1" or "date" in msg:
            if state.intent == "BOOK":
                state.date = None
                state.time = None
                state.stage = FlowStage.BOOK_DATE
                return "Sure — what new date would you like?"

            if state.intent == "RESCHEDULE":
                state.reschedule_date = None
                state.reschedule_time = None
                state.stage = FlowStage.RESCHEDULE_DATE
                return "Sure — what new date would you like?"

        # Change TIME
        if msg == "2" or "time" in msg:
            if state.intent == "BOOK":
                state.time = None
                state.stage = FlowStage.BOOK_TIME
                return "Sure — what new time would you prefer?"

            if state.intent == "RESCHEDULE":
                state.reschedule_time = None
                state.stage = FlowStage.RESCHEDULE_TIME
                return "Sure — what new time would you prefer?"

        # Change TREATMENT (booking only)
        if msg == "3" or "treatment" in msg:
            if state.intent == "BOOK":
                state.treatment_key = None
                state.stage = FlowStage.BOOK_TREATMENT
                return "Sure — what treatment do you need?\n" + list_treatments_for_display()

        return "Please choose:\n1️⃣ Date\n2️⃣ Time\n3️⃣ Treatment"

    # ---------------------------
    # CANCEL
    # ---------------------------
    if state.intent == "CANCEL":

        # STEP 1: CONFIRM CANCELLATION
        if state.stage == FlowStage.CANCEL_CONFIRM:
            if msg not in CONTROL_WORDS:
                return (
                    "Please confirm:\n"
                    "Reply *yes* to proceed or *no* to go back."
                )

            try:
                cancel_appointment_by_id(
                    state.selected_appointment_id,
                    doctor_id
                )

                logger.info(
                    f"Appointment cancelled | doctor_id={doctor_id} | "
                    f"appointment_id={state.selected_appointment_id}"
                )
            except Exception:
                state.reset_flow()
                return (
                    "⚠️ I couldn't cancel the appointment right now.\n"
                    "Please try again in a moment."
                )

            state.reset_flow()
            return "✅ Your appointment has been cancelled."

        # STEP 2: GET PATIENT PHONE
        if not state.patient_phone:
            digits = re.sub(r"\D", "", msg)
            if len(digits) == 10:
                state.patient_phone = digits
            else:
                return "Please tell me the phone number used while booking."

        # STEP 3: FETCH ACTIVE APPOINTMENTS
        if state.candidate_appointments is None:
            appts = get_active_appointments_by_phone(
                phone=state.patient_phone,
                doctor_id=doctor_id,
            )

            if not appts:
                state.reset_flow()
                return "You don't have any active appointments."

            state.candidate_appointments = appts

            if len(appts) == 1:
                chosen = appts[0]

                # 24-HOUR CUTOFF CHECK
                IST = pytz.timezone("Asia/Kolkata")
                now = datetime.now(IST)

                appt_datetime = datetime.combine(
                    chosen.appointment_date,
                    chosen.appointment_time
                )
                appt_datetime = IST.localize(appt_datetime)

                if appt_datetime - now < timedelta(hours=24):
                    db = SessionLocal()
                    try:
                        doctor = get_doctor_by_id(db, doctor_id)
                    finally:
                        db.close()

                    clinic_phone = doctor.clinic_phone_number or doctor.doctor_whatsapp_number or "the clinic"

                    state.reset_flow()
                    return (
                        "⚠️ Online cancellation is not allowed within 24 hours of the appointment.\n\n"
                        f"📞 Please contact the clinic directly at {clinic_phone}."
                    )

                state.selected_appointment_id = chosen.appointment_id
                state.stage = FlowStage.CANCEL_CONFIRM

                return (
                    f"You have one appointment on "
                    f"{chosen.appointment_date} at "
                    f"{chosen.appointment_time.strftime('%H:%M')}.\n"
                    "Do you want to cancel it? (yes / no)"
                )

            else:
                lines = ["Here are your active appointments:"]
                for i, a in enumerate(appts, 1):
                    lines.append(
                        f"{i}️⃣ {a.appointment_date} at {a.appointment_time.strftime('%H:%M')}"
                    )
                lines.append("Please tell me which one you want to cancel.")
                return "\n".join(lines)

        # STEP 4: USER SELECTS APPOINTMENT
        if not state.selected_appointment_id:
            m = re.search(r"\b(\d+)\b", msg)
            if not m:
                return "Please choose an option number."

            idx = int(m.group(1)) - 1
            if not (0 <= idx < len(state.candidate_appointments)):
                return "Please choose a valid option number."

            chosen = state.candidate_appointments[idx]

            # 24-HOUR CUTOFF CHECK
            IST = pytz.timezone("Asia/Kolkata")
            now = datetime.now(IST)

            appt_datetime = datetime.combine(
                chosen.appointment_date,
                chosen.appointment_time
            )
            appt_datetime = IST.localize(appt_datetime)

            if appt_datetime - now < timedelta(hours=24):
                db = SessionLocal()
                try:
                    doctor = get_doctor_by_id(db, doctor_id)
                finally:
                    db.close()

                clinic_phone = doctor.clinic_phone_number or doctor.doctor_whatsapp_number or "the clinic"

                state.reset_flow()
                return (
                    "⚠️ Online cancellation is not allowed within 24 hours of the appointment.\n\n"
                    f"📞 Please contact the clinic directly at {clinic_phone}."
                )

            state.selected_appointment_id = chosen.appointment_id
            state.stage = FlowStage.CANCEL_CONFIRM

            return (
                f"You have selected the appointment on "
                f"{chosen.appointment_date} at "
                f"{chosen.appointment_time.strftime('%H:%M')}.\n"
                "Do you want to cancel it? (yes / no)"
            )

    # ---------------------------
    # RESCHEDULE (STATE-DRIVEN)
    # ---------------------------
    elif state.intent == "RESCHEDULE":

        # STEP 1: SELECT APPOINTMENT
        if state.stage == FlowStage.RESCHEDULE_SELECT:

            if state.candidate_appointments is None:
                phone = re.sub(r"\D", "", msg)
                if len(phone) != 10:
                    return "Please share the 10-digit number used for booking."

                appts = get_active_appointments_by_phone(
                    phone=phone,
                    doctor_id=doctor_id,
                )

                if not appts:
                    state.reset_flow()
                    return "❌ No active appointments found for this number."

                state.candidate_appointments = appts

                if len(appts) == 1:
                    chosen = appts[0]

                    # 24-HOUR EARLY BLOCK
                    IST = pytz.timezone("Asia/Kolkata")
                    now = datetime.now(IST)

                    appt_datetime = datetime.combine(
                        chosen.appointment_date,
                        chosen.appointment_time
                    )
                    appt_datetime = IST.localize(appt_datetime)

                    if appt_datetime - now < timedelta(hours=24):
                        db = SessionLocal()
                        try:
                            doctor = get_doctor_by_id(db, doctor_id)
                        finally:
                            db.close()

                        clinic_phone = doctor.clinic_phone_number or doctor.doctor_whatsapp_number or "the clinic"

                        state.reset_flow()
                        return (
                            "⚠️ Online rescheduling is not allowed within 24 hours of the appointment.\n\n"
                            f"📞 Please contact the clinic directly at {clinic_phone}."
                        )

                    state.selected_appointment_id = chosen.appointment_id
                    state.stage = FlowStage.RESCHEDULE_DATE
                    return "What new date would you like?"

                options = "\n".join(
                    f"{i+1}. {a.appointment_date} at {a.appointment_time.strftime('%H:%M')}"
                    for i, a in enumerate(appts)
                )
                return f"Which appointment would you like to reschedule?\n{options}"

            if state.selected_appointment_id is None:
                try:
                    idx = int(msg.strip()) - 1
                    chosen = state.candidate_appointments[idx]

                    # 24-HOUR EARLY BLOCK
                    IST = pytz.timezone("Asia/Kolkata")
                    now = datetime.now(IST)

                    appt_datetime = datetime.combine(
                        chosen.appointment_date,
                        chosen.appointment_time
                    )
                    appt_datetime = IST.localize(appt_datetime)

                    if appt_datetime - now < timedelta(hours=24):
                        db = SessionLocal()
                        try:
                            doctor = get_doctor_by_id(db, doctor_id)
                        finally:
                            db.close()

                        clinic_phone = doctor.clinic_phone_number or doctor.doctor_whatsapp_number or "the clinic"

                        state.reset_flow()
                        return (
                            "⚠️ Online rescheduling is not allowed within 24 hours of the appointment.\n\n"
                            f"📞 Please contact the clinic directly at {clinic_phone}."
                        )

                    state.selected_appointment_id = chosen.appointment_id
                    state.stage = FlowStage.RESCHEDULE_DATE
                    return "What new date would you like?"

                except Exception:
                    return "Please reply with the number corresponding to the appointment above."

        # STEP 2: NEW DATE
        if state.stage == FlowStage.RESCHEDULE_DATE:
            parsed = normalize_date(msg)

            if not parsed:
                return "Sure 🙂 What date would you like to reschedule to?"

            if not is_working_day(parsed, doctor_id):
                return (
                    "❌ The doctor is not available on that date.\n"
                    "Please choose another day."
                )

            state.reschedule_date = parsed
            state.stage = FlowStage.RESCHEDULE_TIME
            return "And what time works best for you?"

        # STEP 3: NEW TIME
        if state.stage == FlowStage.RESCHEDULE_TIME:
            t, needs_clarification = normalize_time(extracted["time_text"] or msg)

            if needs_clarification:
                return (
                    "I didn't catch the time clearly.\n"
                    "Please reply like: 3pm or 3:30pm."
                )

            if not t:
                return "Could you please tell me the preferred time?"

            if not is_within_clinic_hours(t, doctor_id):
                db = SessionLocal()
                try:
                    doctor = get_doctor_by_id(db, doctor_id)
                finally:
                    db.close()
                return (
                    "❌ The doctor is not available at that time.\n\n"
                    f"🕒 Clinic hours are "
                    f"{doctor.work_start_time.strftime('%H:%M')} to "
                    f"{doctor.work_end_time.strftime('%H:%M')}."
                )

            if not check_availability(
                state.reschedule_date,
                t,
                doctor_id,
                exclude_appointment_id=state.selected_appointment_id,
            ):
                return (
                    "❌ That time slot is not available.\n"
                    "Please choose a different time."
                )

            state.reschedule_time = t
            state.stage = FlowStage.RESCHEDULE_CONFIRM

        # STEP 4: CONFIRM
        if state.stage == FlowStage.RESCHEDULE_CONFIRM:
            if msg == "no":
                state.stage = FlowStage.CHANGE_CHOICE
                return (
                    "What would you like to change?\n"
                    "1️⃣ Date\n"
                    "2️⃣ Time\n"
                    "Or say *start over*"
                )

            if msg not in CONTROL_WORDS:
                return (
                    f"Please confirm rescheduling to:\n"
                    f"📅 {state.reschedule_date}\n"
                    f"⏰ {state.reschedule_time}\n"
                    f"(yes / no)"
                )

            selected_appt = next(
                a for a in state.candidate_appointments
                if a.appointment_id == state.selected_appointment_id
            )

            existing_event_id = selected_appt.calendar_event_id

            if not existing_event_id:
                state.reset_flow()
                return (
                    "⚠️ This appointment cannot be rescheduled because "
                    "it is not linked to a calendar event."
                )

            try:
                update_calendar_event(
                    doctor_id=doctor_id,
                    event_id=existing_event_id,
                    new_date=state.reschedule_date,
                    new_time=state.reschedule_time,
                )
            except Exception:
                state.reset_flow()
                return (
                    "⚠️ The appointment was updated, but we couldn't update the calendar right now.\n"
                    "The clinic has been notified."
                )

            reschedule_appointment_db(
                appointment_id=state.selected_appointment_id,
                new_date=state.reschedule_date,
                new_time=state.reschedule_time,
                new_calendar_event_id=existing_event_id,
            )

            logger.info(
                f"Appointment rescheduled | doctor_id={doctor_id} | "
                f"appointment_id={state.selected_appointment_id}"
            )

            state.reset_flow()
            return "✅ Appointment rescheduled successfully."

    # ---------------------------
    # BOOK (STATE-DRIVEN)
    # ---------------------------
    elif state.intent == "BOOK":

        # STEP 0: TREATMENT
        if state.stage == FlowStage.BOOK_TREATMENT:
            # Try extracted treatment_key first
            treatment_key = extracted.get("treatment_key")

            # If not extracted, try direct alias match on raw message
            if not treatment_key:
                treatment = get_treatment_by_alias(user_message)
                if treatment:
                    treatment_key = treatment.key

            # If user typed a number, map it to catalogue index
            num_match = re.search(r"\b(\d+)\b", msg)
            if num_match and not treatment_key:
                idx = int(num_match.group(1)) - 1
                if 0 <= idx < len(TREATMENT_CATALOGUE):
                    treatment_key = TREATMENT_CATALOGUE[idx].key

            if treatment_key:
                state.treatment_key = treatment_key
                treatment = get_treatment_by_key(treatment_key)
                state.stage = FlowStage.BOOK_DATE
                return (
                    f"Got it! 🦷\n\n"
                    f"*{treatment.display_name}*\n"
                    f"⏱ Duration: {treatment.duration_minutes} min\n\n"
                    f"What date would you like to book?"
                )
            else:
                return (
                    "What type of treatment do you need?\n"
                    + list_treatments_for_display()
                    + "\n\nReply with the name or the number."
                )

        # STEP 1: DATE
        if state.stage == FlowStage.BOOK_DATE:
            parsed = normalize_date(msg)

            IST = pytz.timezone("Asia/Kolkata")
            today = datetime.now(IST).date()

            if not parsed:
                return "What date would you like to book?"

            parsed_date = datetime.strptime(parsed, "%Y-%m-%d").date()

            if parsed_date < today:
                return "❌ You cannot book for a past date. Please choose a valid date."

            if parsed_date > today + timedelta(days=7):
                return "📅 Appointments can only be booked up to 7 days in advance."

            if not is_working_day(parsed, doctor_id):
                return (
                    "❌ The doctor is not available on that date.\n"
                    "Please choose another day."
                )

            state.date = parsed
            state.stage = FlowStage.BOOK_TIME
            return "What time would you prefer?"

        # STEP 2: TIME
        if state.stage == FlowStage.BOOK_TIME:
            t, needs_clarification = normalize_time(extracted["time_text"] or msg)

            if needs_clarification:
                return "Please specify the exact time (e.g., 3pm)."

            if not t:
                return "Could you please specify the exact time?"

            if not is_within_clinic_hours(t, doctor_id):
                db = SessionLocal()
                try:
                    doctor = get_doctor_by_id(db, doctor_id)
                finally:
                    db.close()
                return (
                    "❌ The doctor is not available at that time.\n\n"
                    f"🕒 Clinic hours are "
                    f"{doctor.work_start_time.strftime('%H:%M')} to "
                    f"{doctor.work_end_time.strftime('%H:%M')}."
                )

            if not check_availability(state.date, t, doctor_id):
                return (
                    "❌ That time slot is not available.\n"
                    "Please choose a different time."
                )

            state.time = t
            state.stage = FlowStage.BOOK_CONFIRM
            return "May I know the patient's name?"

        # STEP 3: NAME
        if state.stage == FlowStage.BOOK_CONFIRM and not state.patient_name:
            if confidence == "high" and extracted["patient_name"]:
                state.patient_name = extracted["patient_name"].title()
            elif msg not in CONTROL_WORDS and not re.search(r"\d", msg):
                state.patient_name = user_message.strip().title()
            else:
                return "May I know the patient's name?"

        # STEP 4: PHONE
        if state.stage == FlowStage.BOOK_CONFIRM and not state.patient_phone:
            if confidence == "high" and extracted["patient_phone"]:
                digits = re.sub(r"\D", "", extracted["patient_phone"])
            else:
                digits = re.sub(r"\D", "", msg)

            if len(digits) != 10:
                return "Please share a 10-digit contact number."

            state.patient_phone = digits

        # STEP 5: CONFIRM
        if state.stage == FlowStage.BOOK_CONFIRM:
            if msg == "no":
                state.stage = FlowStage.CHANGE_CHOICE
                return (
                    "What would you like to change?\n"
                    "1️⃣ Date\n"
                    "2️⃣ Time\n"
                    "3️⃣ Treatment"
                )

            # Build confirm display with treatment info
            treatment = get_treatment_by_key(state.treatment_key) if state.treatment_key else None
            treatment_line = (
                f"\n🦷 Treatment: {treatment.display_name}\n"
                f"⏱ Duration: {treatment.duration_minutes} min"
                if treatment else ""
            )

            if msg not in CONTROL_WORDS:
                return (
                    f"Please confirm your appointment:\n\n"
                    f"📅 Date: {state.date}\n"
                    f"⏰ Time: {state.time}\n"
                    f"{treatment_line}\n"
                    f"👤 Patient: {state.patient_name}\n"
                    f"📞 Phone: {state.patient_phone}\n\n"
                    f"Reply *yes* to confirm or *no* to change something."
                )

            try:
                booking = book_appointment(
                    state.date,
                    state.time,
                    doctor_id,
                    state.patient_name,
                    state.patient_phone,
                    treatment_key=state.treatment_key,
                )
                logger.info(
                    f"Booking created | doctor_id={doctor_id} | "
                    f"date={state.date} | time={state.time} | "
                    f"treatment={state.treatment_key}"
                )

            except Exception as e:
                state.reset_flow()
                return f"❌ Booking failed: {str(e)}"

            state.last_appointment_id = booking["appointment_id"]
            state.last_event_id = booking["event_id"]
            state.last_doctor_id = doctor_id
            state.last_date = booking["date"]
            state.last_time = booking["time"]
            state.last_patient_name = state.patient_name
            state.last_patient_phone = state.patient_phone

            # Build success message
            treatment_confirm_line = ""
            if booking.get("treatment"):
                treatment_confirm_line = (
                    f"\n🦷 Treatment: {booking['treatment']}\n"
                    f"⏱ Duration: {booking['duration_minutes']} min"
                )

            state.reset_flow()

            return (
                f"✅ Appointment Confirmed!\n\n"
                f"📅 Date: {booking['date']}\n"
                f"⏰ Time: {booking['time']}"
                f"{treatment_confirm_line}\n\n"
                f"You can say *cancel*, *reschedule*, or *book another appointment*."
            )

        # 🛡️ FINAL SAFETY NET
        return "I didn't quite get that. Could you please rephrase?"