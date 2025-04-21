import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from pocket_clinic_tools.referral_dispatcher import ReferralDispatcherTools

load_dotenv()

if __name__ == "__main__":
    input_data = {
        "phone_number": os.getenv("TEST_RECEIVER_PHONE", "+234XXXXXXXXXX"),
        "triage_summary": "Likely malaria. Please visit a clinic within 24 hours."
    }

    result = ReferralDispatcherTools.send_referral.invoke({'input_data': input_data})
    print("SMS Dispatch Result:", result)
