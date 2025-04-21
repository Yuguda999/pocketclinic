from os import getenv
from textwrap import dedent
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from langchain_openai import ChatOpenAI
from twilio.rest import Client

# ——— Load environment ———
from dotenv import load_dotenv
load_dotenv()
TWILIO_SID   = getenv("TWILIO_SID")
TWILIO_TOKEN = getenv("TWILIO_TOKEN")
TWILIO_FROM  = getenv("TWILIO_FROM")

# Initialize Twilio client - with error handling
try:
    twilio = Client(TWILIO_SID, TWILIO_TOKEN)
    print(f"Twilio client initialized with SID: {TWILIO_SID[:5]}... and FROM: {TWILIO_FROM}")
except Exception as e:
    print(f"Error initializing Twilio client: {str(e)}")
    twilio = None

# Set up OpenAI model
OpenAIGPT4 = ChatOpenAI(
    model="gpt-4"
)

# ——— FastAPI & Schema ———
app = FastAPI(title="PocketClinic Triage Service")

class TriageRequest(BaseModel):
    phone: str
    text: str
    audio_url: Optional[str] = None

# ——— Direct LLM Functions (no tools) ———
def analyze_symptoms(text: str) -> Dict[str, Any]:
    """Analyze symptoms from text using LLM"""
    try:
        prompt = f"""
        You are a medical symptom analyzer for a remote Nigerian clinic.

        Patient message: "{text}"

        Extract and categorize symptoms from this message. If no specific symptoms are mentioned,
        use your medical knowledge to interpret the message.

        Return your analysis as a JSON with:
        - 'symptoms': a list of symptoms mentioned
        - 'duration_days': estimated duration in days (default to 1 if unknown)
        - 'severity': severity level (mild, moderate, severe) based on the description
        """
        
        response = OpenAIGPT4.invoke(prompt)
        
        # Try to extract JSON from the response
        try:
            result = json.loads(response.content)
            if 'symptoms' in result:
                return result
        except:
            # If JSON parsing fails, try to extract information manually
            import re
            # Fallback extraction
            symptoms_match = re.search(r'symptoms.*?[\[\"]([^\]\"]+)', response.content, re.DOTALL | re.IGNORECASE)
            duration_match = re.search(r'duration_days.*?[:\s]+(\d+)', response.content, re.IGNORECASE)
            severity_match = re.search(r'severity.*?[:\s]+["\']*([a-z]+)', response.content, re.IGNORECASE)
            
            symptoms = symptoms_match.group(1).split(',') if symptoms_match else ["unspecified symptoms"]
            duration = int(duration_match.group(1)) if duration_match else 1
            severity = severity_match.group(1) if severity_match else "moderate"
            
            return {
                "symptoms": [s.strip() for s in symptoms],
                "duration_days": duration,
                "severity": severity
            }
    except Exception as e:
        print(f"[ERROR] Failed to process input text: {str(e)}")
        return {
            "symptoms": ["unspecified symptoms"],
            "duration_days": 1,
            "severity": "moderate"
        }

def triage_symptoms(symptoms_text: str) -> Dict[str, str]:
    """Determine condition and action based on symptom text"""
    try:
        prompt = f"""
        You are a medical triage expert in a remote Nigerian clinic.
        
        Patient symptoms: {symptoms_text}
        
        Based on these symptoms and considering regional disease prevalence in Nigeria,
        determine:
        1. The most likely condition
        2. The recommended action (treat locally or refer)
        
        Focus on common conditions in Nigeria such as malaria, typhoid, respiratory infections, 
        and diarrheal diseases. Consider WHO IMCI guidelines.
        
        Return your analysis as a JSON with 'condition' and 'action' fields.
        """
        
        response = OpenAIGPT4.invoke(prompt)
        content = response.content
        
        # Try to extract JSON from the response
        try:
            # First, check if the entire response is valid JSON
            result = json.loads(content)
            if 'condition' in result and 'action' in result:
                return result
        except:
            pass
            
        # If that fails, try to find JSON inside the text
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(0))
                if 'condition' in result and 'action' in result:
                    return result
            except:
                pass
        
        # If we still can't parse JSON, extract information manually
        condition_match = re.search(r'condition["\s:]+([^"}\n,]+)', content, re.IGNORECASE)
        action_match = re.search(r'action["\s:]+([^"}\n,]+)', content, re.IGNORECASE)
        
        condition = condition_match.group(1).strip() if condition_match else "unidentified condition"
        action = action_match.group(1).strip() if action_match else "seek medical attention"
        
        return {
            "condition": condition,
            "action": action
        }
    except Exception as e:
        print(f"[ERROR] Triage analysis failed: {str(e)}")
        # Fallback response
        return {
            "condition": "unidentified condition",
            "action": "seek medical attention immediately"
        }

def generate_and_send_sms(phone: str, condition: str, action: str) -> Dict[str, str]:
    """Generate and send SMS message"""
    try:
        # Use the LLM to generate a tailored message
        prompt = f"""
        You are a healthcare provider in Nigeria sending a critical SMS to a patient.
        
        Diagnosed condition: {condition}
        Recommended action: {action}
        
        Create a clear, concise SMS (max 160 characters) that:
        1. Communicates the diagnosis with appropriate urgency
        2. Gives specific instructions on the recommended action
        3. Is culturally appropriate for Nigeria
        4. Includes where to follow up if needed
        
        Just return the SMS text with no additional formatting or explanation.
        """
        
        response = OpenAIGPT4.invoke(prompt)
        sms_text = response.content.strip()
        
        # Ensure text isn't too long for SMS
        if len(sms_text) > 160:
            sms_text = sms_text[:157] + "..."
        
        if not twilio:
            print(f"[INFO] Twilio not configured. Would have sent: {sms_text}")
            return {
                "status": "simulation",
                "message_text": sms_text
            }
            
        if not phone:
            return {
                "status": "error",
                "message": "No phone number provided",
                "message_text": sms_text
            }
            
        # Send the actual SMS
        msg = twilio.messages.create(
            body=sms_text,
            from_=TWILIO_FROM,
            to=phone
        )
        
        print(f"[SUCCESS] SMS sent to {phone}: {sms_text}")
        return {
            "status": "sent",
            "message_id": msg.sid,
            "message_text": sms_text
        }
        
    except Exception as e:
        print(f"[ERROR] SMS dispatch failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "message_text": f"ALERT: You may have {condition}. {action}."
        }

def get_symptoms_as_text(symptoms_data):
    """Convert symptoms data to a simple text string"""
    if isinstance(symptoms_data, dict):
        text_parts = []
        if 'symptoms' in symptoms_data and isinstance(symptoms_data['symptoms'], list):
            text_parts.append(", ".join(symptoms_data['symptoms']))
        if 'duration_days' in symptoms_data:
            text_parts.append(f"for {symptoms_data['duration_days']} days")
        if 'severity' in symptoms_data:
            text_parts.append(f"with {symptoms_data['severity']} severity")
        return " ".join(text_parts)
    elif isinstance(symptoms_data, list):
        return ", ".join(symptoms_data)
    elif isinstance(symptoms_data, str):
        return symptoms_data
    else:
        return "unspecified symptoms"

# ——— Endpoint ———
@app.post("/triage")
async def run_triage(req: TriageRequest):
    try:
        # Extract message content
        text = req.text
        phone = req.phone
        
        print(f"[INFO] Processing request from {phone} with text: {text}")
        
        # Step 1: Analyze symptoms from text
        symptoms_data = analyze_symptoms(text)
        print(f"[INFO] Extracted symptoms: {symptoms_data}")
        
        # Convert to text representation
        symptoms_text = get_symptoms_as_text(symptoms_data)
        print(f"[INFO] Symptoms text: {symptoms_text}")
        
        # Step 2: Determine condition and recommended action
        triage_result = triage_symptoms(symptoms_text)
        print(f"[INFO] Triage result: {triage_result}")
        
        # Step 3: Generate and send SMS with results
        sms_result = generate_and_send_sms(
            phone=phone,
            condition=triage_result.get("condition", "unidentified condition"),
            action=triage_result.get("action", "seek medical attention")
        )
        print(f"[INFO] SMS result: {sms_result}")
        
        # Return complete response
        return {
            "status": "completed",
            "symptoms": symptoms_data,
            "triage": triage_result,
            "sms_status": sms_result
        }
    except Exception as e:
        # Print detailed error information for debugging
        import traceback
        print("[ERROR] API exception:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))