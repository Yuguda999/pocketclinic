from crewai import Agent
from textwrap import dedent
from langchain_openai import ChatOpenAI
from pocket_clinic_tools.symptom_collector import collect_symptoms
from pocket_clinic_tools.triage_symptoms import triage_symptoms
from pocket_clinic_tools.referral_dispatcher import send_referral

class PocketClinicAgents:
    def __init__(self):
        self.OpenAIGPT4 = ChatOpenAI(name="gpt-4o", temperature=0.7)
    
    def symptom_collector_agent(self):
        return Agent(
            role="Symptom Collector Agent",
            backstory=dedent("""
                You are the Symptom Collector Agent. Your job is to convert
                a short voice clip or SMS text from a health worker into a
                structured symptom list following the IMCI protocol.
            """),
            goal="Given an audio clip or SMS text, produce a dict like {'fever': True, 'cough': False, ...}.",
            tools=[collect_symptoms],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT4,
        )

    def triage_decision_agent(self):
        return Agent(
            role="Triage Decision Agent",
            backstory=dedent("""
                You are the Triage Decision Agent, trained on WHO IMCI protocols.
                You take a structured symptom list and decide whether the patient
                likely has malaria, needs referral for pneumonia, or is all clear.
            """),
            goal=dedent("""
                Given a dict of symptoms (e.g. {'fever': True, 'cough': False, ...}),
                output exactly one of:
                  - "Likely malaria"
                  - "Refer for pneumonia"
                  - "All clear"
            """),
            tools=[triage_symptoms],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT4,
        )

    def referral_dispatcher_agent(self):
        return Agent(
            role="Referral Dispatcher Agent",
            backstory=dedent("""
                You are the Referral Dispatcher Agent. You receive a triage decision
                (e.g. "Likely malaria") plus a phone number, and must send an SMS
                containing the result and a teleconsult link.
            """),
            goal=dedent("""
                Given {'phone_number': '+23480…', 'triage_summary': "Likely malaria"},
                call the Twilio tool to send the SMS and return the Twilio SID.
            """),
            tools=[send_referral],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT4,
        )
    