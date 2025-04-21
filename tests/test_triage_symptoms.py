import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pocket_clinic_tools.symptom_collector import SymptomCollectorTools
from pocket_clinic_tools.triage_symptoms import SymptomTriageTools

if __name__ == "__main__":
    txt = "Patient has had fever and cough for 4 days."

    collected = SymptomCollectorTools.collect_symptoms.invoke({"input_data": {"text_message": txt}})
    print("Collected Symptoms:", collected)

    triaged = SymptomTriageTools.triage_symptoms.invoke({"input_data": collected})
    print("Triage Result:", triaged)
