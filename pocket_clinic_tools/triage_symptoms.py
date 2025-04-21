# pocket_clinic_tools/triage_symptoms.py

from crewai.tools import tool

@tool("Triage Symptoms")
def triage_symptoms(
    fever: bool = False,
    cough: bool = False,
    difficulty_breathing: bool = False,
    diarrhea: bool = False,
    duration_days: int = 0
) -> dict:
    """
    Assess symptom severity and return an urgency level plus recommendation.

    Args:
      fever: whether the patient has a fever
      cough: whether the patient has a cough
      difficulty_breathing: whether the patient has difficulty breathing
      diarrhea: whether the patient has diarrhea
      duration_days: how many days the symptoms have lasted

    Returns:
      A dict with:
        - 'urgency': 'low' | 'moderate' | 'critical'
        - 'recommendation': next‐step advice
    """
    # Rule‑based triage
    if difficulty_breathing or duration_days > 4:
        urgency = "critical"
        recommendation = "Seek emergency medical attention immediately."
    elif fever or cough or diarrhea:
        urgency = "moderate"
        recommendation = "Visit a clinic if symptoms persist more than 2 days."
    else:
        urgency = "low"
        recommendation = "Monitor symptoms at home and rest."

    return {
        "urgency": urgency,
        "recommendation": recommendation
    }
