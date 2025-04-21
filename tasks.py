from crewai import Task
from textwrap import dedent

class PocketClinicTasks:
    def __tip_section(self):
        return "Deliver accurate results quickly—this directly impacts patient outcomes!"

    def collect_symptoms_task(self, agent, text_message, audio_clip_b64):
        return Task(
            description=dedent(f"""
                **Task**: Collect Symptoms
                **Description**: Given either a base64‑encoded audio clip or an SMS text from a health worker,
                convert it into a structured symptom dict following IMCI protocols.
                
                **Parameters**:
                  - text_message: {text_message!r}
                  - audio_clip_b64: {audio_clip_b64!r}
                
                **Note**: {self.__tip_section()}
            """),
            expected_output="A dict of symptoms (e.g. {'fever': True, 'cough': False, ...}).",
            agent=agent,
        )

    def triage_decision_task(self, agent, symptoms):
        return Task(
            description=dedent(f"""
                **Task**: Triage Decision
                **Description**: Using the structured symptom dict, decide one of:
                  - "Likely malaria"
                  - "Refer for pneumonia"
                  - "All clear"
                based on WHO IMCI protocols.
                
                **Parameters**:
                  - symptoms: {symptoms}
                
                **Note**: {self.__tip_section()}
            """),
            expected_output="A dict with: {'urgency': 'low' | 'moderate' | 'critical', 'recommendation': str}",
            agent=agent,
        )

    def dispatch_referral_task(self, agent, phone_number, triage_summary):
        return Task(
            description=dedent(f"""
                **Task**: Dispatch Referral
                **Description**: Send an SMS to the given phone number with the triage result
                and a teleconsultation link via Twilio.
                
                **Parameters**:
                  - phone_number: {phone_number}
                  - triage_summary: {triage_summary!r}
                
                **Note**: {self.__tip_section()}
            """),
            expected_output="A string like 'Referral sent to +2348012345678. SID: XXXXX'",
            agent=agent,
        )
