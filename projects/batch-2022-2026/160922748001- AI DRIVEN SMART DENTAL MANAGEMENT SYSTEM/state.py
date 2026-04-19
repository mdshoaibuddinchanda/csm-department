# state.py

from enum import Enum, auto


class FlowStage(Enum):
    """
    Authoritative conversation stages.
    The agent MUST rely on this to decide behavior.
    """

    # Global
    IDLE = auto()
    INTENT_CONFIRM_SWITCH = auto()

    # Booking flow
    BOOK_TREATMENT = auto()   # collect treatment type before date
    BOOK_DATE = auto()
    BOOK_TIME = auto()
    BOOK_CONFIRM = auto()

    # Cancellation flow
    CANCEL_PHONE = auto()
    CANCEL_SELECT = auto()
    CANCEL_CONFIRM = auto()

    # Reschedule flow
    RESCHEDULE_SELECT = auto()
    RESCHEDULE_DATE = auto()
    RESCHEDULE_TIME = auto()
    RESCHEDULE_CONFIRM = auto()

    CHANGE_CHOICE = auto()  # for changing date/time during confirm stages


class BookingState:
    def __init__(self):
        # ------------------
        # Conversation control
        # ------------------
        self.intent: str | None = None          # BOOK | CANCEL | RESCHEDULE
        self.stage: FlowStage = FlowStage.IDLE

        # ------------------
        # Doctor context (required)
        # ------------------
        self.doctor_id = None
        self.doctor_name = None

        # ------------------
        # Booking data (in-progress)
        # ------------------
        self.treatment_key: str | None = None   # e.g. "root_canal"
        self.date = None
        self.time = None
        self.patient_name = None
        self.patient_phone = None

        # ------------------
        # Cancellation / Reschedule data
        # ------------------
        self.candidate_appointments = None      # list[Appointment]
        self.selected_appointment_id = None

        # Reschedule-specific
        self.reschedule_date = None
        self.reschedule_time = None

        # ------------------
        # Last confirmed appointment (fast-path UX)
        # ------------------
        self.last_appointment_id = None
        self.last_event_id = None
        self.last_doctor_id = None
        self.last_date = None
        self.last_time = None
        self.last_patient_name = None
        self.last_patient_phone = None

        # ------------------
        # Misc helpers
        # ------------------
        self.greeted = False
        self.pending_intent_switch: str | None = None  # for confirmation flow

        self._reschedule_initialized = False


    # -------------------------------------------------
    # Reset helpers (VERY IMPORTANT)
    # -------------------------------------------------

    def reset_flow(self):
        """
        Full reset of conversation flow.
        Doctor context is preserved.
        """
        self.intent = None
        self.stage = FlowStage.IDLE

        self.treatment_key = None
        self.date = None
        self.time = None
        self.patient_name = None
        self.patient_phone = None

        self.candidate_appointments = None
        self.selected_appointment_id = None

        self.reschedule_date = None
        self.reschedule_time = None

        self.pending_intent_switch = None

    def reset_booking(self):
        """
        Reset only booking-related fields.
        """
        self.treatment_key = None
        self.date = None
        self.time = None
        self.patient_name = None
        self.patient_phone = None

    def reset_cancel_reschedule(self):
        """
        Reset cancellation / reschedule selection state.
        """
        self.candidate_appointments = None
        self.selected_appointment_id = None
        self.reschedule_date = None
        self.reschedule_time = None
        self.pending_intent_switch = None


    def is_done(self) -> bool:
        return self.stage == FlowStage.IDLE