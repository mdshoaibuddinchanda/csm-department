from auth_utils import hash_password
from db.repository import create_doctor_auth, get_doctor_by_email

# CHANGE THIS to an existing onboarded doctor's email
EMAIL = "mustafataj13@gmail.com"
PASSWORD = "initialPassword123"

doctor = get_doctor_by_email(EMAIL)
print("Doctor fetched:", doctor)

if not doctor:
    raise RuntimeError(f"No doctor found with email {EMAIL}")

create_doctor_auth(
    doctor_id=doctor.doctor_id,
    email=doctor.email,
    password_hash=hash_password(PASSWORD)
)

print("✅ DoctorAuth created successfully")
