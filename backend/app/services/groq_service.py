import os
import json
from groq import Groq
from flask import current_app


# Default model — fast and capable for medical text generation
GROQ_MODEL = 'llama-3.3-70b-versatile'


def get_groq_client():
    """Initialize and return a Groq client."""
    api_key = current_app.config.get('GROQ_API_KEY') or os.getenv('GROQ_API_KEY')
    if not api_key or api_key == 'your-groq-api-key-here':
        raise ValueError("Groq API key is not configured. Please set GROQ_API_KEY in your .env file.")
    return Groq(api_key=api_key)


def _clean_json_response(text):
    """Strip markdown code fences from an LLM JSON response."""
    text = text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1] if '\n' in text else text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return text.strip()


def analyze_symptoms(symptoms, duration, severity, age, gender, medical_history=''):
    """
    Analyze symptoms and generate medical recommendations using Groq AI.
    Returns a dict with ai_analysis, medication_recs, and food_recs.
    """
    client = get_groq_client()

    system_prompt = (
        "You are ShifaBot, an AI-powered medical diagnosis expert system. "
        "You analyse patient symptoms and return structured medical assessments. "
        "Always respond with valid JSON only — no markdown, no code fences, no extra text."
    )

    user_prompt = f"""Analyse the following patient information and provide a comprehensive medical assessment.

PATIENT INFORMATION:
- Age: {age}
- Gender: {gender}
- Symptoms: {symptoms}
- Duration of Symptoms: {duration}
- Severity Level: {severity}
- Medical History: {medical_history if medical_history else 'None reported'}

Return your response in this EXACT JSON structure:
{{
    "possible_conditions": ["Condition 1 - brief explanation", "Condition 2 - brief explanation", "Condition 3 - brief explanation"],
    "analysis": "A detailed paragraph analysing the symptoms, their possible causes, and general assessment.",
    "medication_recommendations": ["Specific medication or treatment 1 with dosage if applicable", "Specific medication or treatment 2", "When to see a doctor advice"],
    "food_recommendations": ["Foods to eat recommendation 1", "Foods to eat recommendation 2", "Foods to avoid 1", "General dietary advice"],
    "lifestyle_recommendations": ["Lifestyle advice 1", "Lifestyle advice 2", "Lifestyle advice 3"],
    "warning_signs": ["Warning sign 1", "Warning sign 2", "Warning sign 3"],
    "disclaimer": "This is an AI-generated analysis and should not replace professional medical advice. Please consult a healthcare provider for proper diagnosis and treatment."
}}

IMPORTANT: medication_recommendations, food_recommendations, and lifestyle_recommendations MUST be arrays of individual bullet-point strings, NOT a single paragraph string."""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=2048
        )
        response_text = _clean_json_response(response.choices[0].message.content)

        result = json.loads(response_text)

        # Store array fields as JSON strings for DB storage
        med_recs = result.get('medication_recommendations', [])
        food_recs = result.get('food_recommendations', [])
        lifestyle_recs = result.get('lifestyle_recommendations', [])

        # Ensure they are lists
        if isinstance(med_recs, str):
            med_recs = [med_recs]
        if isinstance(food_recs, str):
            food_recs = [food_recs]
        if isinstance(lifestyle_recs, str):
            lifestyle_recs = [lifestyle_recs]

        # Update the result with proper arrays for the frontend
        result['medication_recommendations'] = med_recs
        result['food_recommendations'] = food_recs
        result['lifestyle_recommendations'] = lifestyle_recs

        return {
            'ai_analysis': json.dumps(result.get('possible_conditions', [])),
            'medication_recs': json.dumps(med_recs),
            'food_recs': json.dumps(food_recs),
            'full_analysis': result
        }

    except json.JSONDecodeError:
        return {
            'ai_analysis': json.dumps([response_text]),
            'medication_recs': 'Please consult a healthcare provider for medication recommendations.',
            'food_recs': 'Please consult a healthcare provider for dietary recommendations.',
            'full_analysis': {
                'analysis': response_text,
                'disclaimer': 'This is an AI-generated analysis and should not replace professional medical advice.'
            }
        }
    except ValueError:
        raise
    except Exception as e:
        return {
            'ai_analysis': json.dumps([f"Error during analysis: {str(e)}"]),
            'medication_recs': 'Unable to generate recommendations at this time.',
            'food_recs': 'Unable to generate recommendations at this time.',
            'full_analysis': {'error': str(e)}
        }


def chatbot_response(conversation_history, user_message, patient_info=None):
    """
    Generate a chatbot response using Groq AI.
    The chatbot intelligently collects symptom information before generating recommendations.
    """
    client = get_groq_client()

    patient_context = ""
    if patient_info:
        patient_context = f"\nCollected patient info so far: {json.dumps(patient_info)}"

    system_prompt = f"""You are ShifaBot, a friendly and professional AI medical assistant. Your job is to:
1. Collect information about the patient's symptoms, duration, severity, age, gender, and medical history through natural conversation.
2. Ask follow-up questions to understand the condition better.
3. Once you have enough information (symptoms, duration, severity, age, gender), provide a brief preliminary assessment.
4. Be empathetic, clear, and professional in your responses.
5. Always remind the patient that you are an AI and they should consult a real doctor for proper diagnosis.

Keep your responses concise (2-4 sentences) unless providing a final assessment.
Ask ONE question at a time to keep the conversation natural.

If you believe you have collected enough information (symptoms, duration, severity, age, gender), end your response with the exact phrase: [READY_FOR_DIAGNOSIS]
{patient_context}"""

    # Build messages list for Groq (OpenAI-compatible format)
    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history:
        messages.append({
            "role": "user" if msg.get('role') == 'user' else "assistant",
            "content": msg.get('content', '')
        })
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=512
        )
        reply = response.choices[0].message.content.strip()

        ready_for_diagnosis = '[READY_FOR_DIAGNOSIS]' in reply
        reply = reply.replace('[READY_FOR_DIAGNOSIS]', '').strip()

        return {
            'reply': reply,
            'ready_for_diagnosis': ready_for_diagnosis
        }
    except Exception as e:
        return {
            'reply': "I'm sorry, I'm having trouble processing your request right now. Please try again.",
            'ready_for_diagnosis': False
        }


def extract_patient_info_from_chat(conversation_history):
    """
    Extract structured patient information from a chatbot conversation using Groq AI.
    """
    client = get_groq_client()

    # Build conversation as a single text block for context
    history_text = ""
    for msg in conversation_history:
        role = "Patient" if msg.get('role') == 'user' else "ShifaBot"
        history_text += f"{role}: {msg.get('content', '')}\n"

    system_prompt = (
        "You are a medical data extraction assistant. "
        "Respond ONLY with valid JSON — no markdown, no code fences, no extra text."
    )

    user_prompt = f"""Based on the following conversation between a patient and ShifaBot medical assistant, extract the patient information.

Conversation:
{history_text}

Return the extracted information in this EXACT JSON structure:
{{
    "symptoms": "description of symptoms mentioned",
    "duration": "how long the symptoms have been present",
    "severity": "mild/moderate/severe",
    "age": "age number or empty string",
    "gender": "male/female/other or empty string",
    "medical_history": "any mentioned medical history or empty string"
}}

If any field is not mentioned in the conversation, use an empty string."""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )
        response_text = _clean_json_response(response.choices[0].message.content)

        info = json.loads(response_text)

        return {
            'symptoms': info.get('symptoms', ''),
            'duration': info.get('duration', ''),
            'severity': info.get('severity', 'moderate'),
            'age': info.get('age', ''),
            'gender': info.get('gender', ''),
            'medical_history': info.get('medical_history', '')
        }
    except Exception:
        return {
            'symptoms': '',
            'duration': '',
            'severity': 'moderate',
            'age': '',
            'gender': '',
            'medical_history': ''
        }
