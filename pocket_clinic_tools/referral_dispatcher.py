# pocket_clinic_tools/referral_dispatcher.py

import os

from crewai.tools import tool
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

@tool("Dispatch Referral via SMS")
def send_referral(
    phone_number: str,
    triage_summary: str
) -> str:
    """
    Send an SMS with the triage result and teleconsult link via Twilio.
    
    Args:
      phone_number: E.164 format (e.g. +2348012345678)
      triage_summary: e.g. "Likely malaria"
    
    Returns:
      Result string or error message.
    """
    sid   = os.getenv("TWILIO_SID")
    token = os.getenv("TWILIO_TOKEN")
    from_ = os.getenv("TWILIO_NUMBER", "+15005550006")
    if not sid or not token:
        return "Error: Twilio credentials not set."

    client = Client(sid, token)
    body = (
        f"Referral Result: {triage_summary}\n"
        "Access Teleconsult: https://teleclinic.ng/consult"
    )
    try:
        msg = client.messages.create(body=body, from_=from_, to=phone_number)
        return f"Referral sent to {phone_number}. SID: {msg.sid}"
    except Exception as e:
        return f"Error sending SMS: {e}"
