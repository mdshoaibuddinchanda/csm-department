from pydantic import BaseModel
from datetime import date, time

class ChatRequest(BaseModel):
    
    message: str
    


class ChatResponse(BaseModel):
    reply: str

class DoctorRescheduleRequest(BaseModel):
    new_date: date
    new_time: time
