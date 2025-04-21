#!/usr/bin/env python3
import os
import sys
import base64
from dotenv import load_dotenv
from pocket_clinic_tools.audio_utils import preprocess_audio

# Allow imports from the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from crewai import Crew
from agents import PocketClinicAgents
from tasks import PocketClinicTasks

class PocketClinicCrew:
    def __init__(self, text_message=None, audio_file=None, phone_number=None):
        self.text_message = text_message
        self.audio_file = audio_file
        self.phone_number = phone_number

    def run(self):
    # 1) Load environment
        load_dotenv()

        # 2) Instantiate agents & tasks
        agents = PocketClinicAgents()
        tasks = PocketClinicTasks()

        collector_agent   = agents.symptom_collector_agent()
        triage_agent      = agents.triage_decision_agent()
        dispatcher_agent  = agents.referral_dispatcher_agent()

        # 3) Prepare audio if provided
        audio_b64 = None
        if self.audio_file:
            # ✅ Preprocess the audio before sending to the LLM
            cleaned_audio_path = preprocess_audio(self.audio_file)
            with open(cleaned_audio_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
                # 4) Build tasks with proper output chaining
        collect_task = tasks.collect_symptoms_task(
            collector_agent,
            text_message=self.text_message,
            audio_clip_b64=audio_b64
        )

        triage_task = tasks.triage_decision_task(
            triage_agent,
            symptoms=collect_task.output  # 👈 use output of collector as input
        )

        dispatch_task = tasks.dispatch_referral_task(
            dispatcher_agent,
            phone_number=self.phone_number,
            triage_summary=triage_task.output  # 👈 use output of triage as input
        )

        # 5) Create & run the Crew
        crew = Crew(
            agents=[collector_agent, triage_agent, dispatcher_agent],
            tasks=[collect_task, triage_task, dispatch_task],
            verbose=True,
        )
        return crew.kickoff()


if __name__ == "__main__":
    load_dotenv()
    print("## PocketClinic Crew AI")
    print("-----------------------")

    text_message = None #"i have fever and cough with diarrhea for 3 days."
    audio_file   = '/home/commanderzer0/Desktop/pocketclinic/tests/audio_samples/symptoms1.wav'
    phone_number = "+2348145243177"

    crew = PocketClinicCrew(
        text_message=text_message,
        audio_file=audio_file,
        phone_number=phone_number,
    )
    result = crew.run()

    print("\n== Crew Run Result ==")
    print(result)
