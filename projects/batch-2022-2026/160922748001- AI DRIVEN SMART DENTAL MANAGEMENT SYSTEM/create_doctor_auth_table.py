from db.database import engine
from db.models import Base, DoctorAuth

print("Creating doctor_auth table...")
Base.metadata.create_all(bind=engine)
print("Done.")
