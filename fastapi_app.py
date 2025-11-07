# Sierra backend (fastapi_app.py)
import os
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import httpx

# Replace with your real secrets
API_KEY = os.environ.get("SIERRA_API_KEY", "demo-secret")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "sk_test_xxx")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
TWILIO_FROM = os.environ.get("TWILIO_FROM_NUMBER")

app = FastAPI(title="Sierra Agent Tools")

def authenticate(key: str | None):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Data models
class AvailabilityRequest(BaseModel):
    start_date: str
    end_date: str
    guests: int
    pets: bool | None = False

class BookingRequest(BaseModel):
    guest_name: str
    email: str
    phone: str
    room_type: str
    start_date: str
    end_date: str
    guests: int
    pets: bool | None = False

class PaymentLinkRequest(BaseModel):
    booking_id: str
    amount: float
    currency: str = "USD"

class SMSRequest(BaseModel):
    phone: str
    message: str

# In-memory store for demo (replace with Supabase/DB)
AVAILABILITY = {
    "Deluxe King": 5,
    "Deluxe Double Queen": 3,
    "Junior Suite": 2,
    "Signature Suite": 1,
    "Penthouse Suite": 0
}
BOOKINGS = {}

# Tool: get_availability
@app.post("/get_availability")
async def get_availability(req: AvailabilityRequest, x_api_key: str | None = Header(None)):
    authenticate(x_api_key)
    # Here you would query Supabase/PMS with req.start_date, req.end_date, etc.
    # For demo, return counts based on dummy inventory
    return {"available_rooms": AVAILABILITY}

# Tool: create_booking
@app.post("/create_booking")
async def create_booking(req: BookingRequest, x_api_key: str | None = Header(None)):
    authenticate(x_api_key)
    booking_id = str(uuid4())
    BOOKINGS[booking_id] = {
        "guest_name": req.guest_name,
        "email": req.email,
        "phone": req.phone,
        "room_type": req.room_type,
        "start_date": req.start_date,
        "end_date": req.end_date,
        "guests": req.guests,
        "pets": req.pets,
        "status": "pending_payment",
        "created_at": datetime.utcnow().isoformat()
    }
    return {"booking_id": booking_id}

# Tool: create_payment_link
@app.post("/create_payment_link")
async def create_payment_link(req: PaymentLinkRequest, x_api_key: str | None = Header(None)):
    authenticate(x_api_key)
    # Normally create a Stripe Checkout Session here
    # For demo, return a fake URL
    fake_url = f"https://checkout.stripe.com/pay/{req.booking_id}"
    # update booking status
    if req.booking_id in BOOKINGS:
        BOOKINGS[req.booking_id]["status"] = "awaiting_payment"
    return {"checkout_url": fake_url}

# Tool: send_text
@app.post("/send_text")
async def send_text(req: SMSRequest, x_api_key: str | None = Header(None)):
    authenticate(x_api_key)
    # Use Twilio REST API to send SMS (mocked here)
    # Example: POST to https://api.twilio.com/2010-04-01/Accounts/{SID}/Messages.json
    print(f"[DEBUG] Sending SMS to {req.phone}: {req.message}")
    return {"status": "sent"}

# Example extra: get_weather (if you decide to implement)
@app.get("/get_weather")
async def get_weather(lat: float, lon: float, x_api_key: str | None = Header(None)):
    authenticate(x_api_key)
    # Call external weather API (OpenWeather/NWS)
    return {"temp_f": 32.0, "summary": "Snow showers", "source": "demo"}

