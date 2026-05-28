import os
import ast
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template

# Initialize Flask application
app = Flask(__name__, template_folder='templates', static_folder='static')

# Define paths for assets
MODEL_PATH = os.path.join("models", "svc.pkl")
DATASETS_DIR = "datasets"

# Load the trained SVC model
try:
    with open(MODEL_PATH, "rb") as f:
        svc_model = pickle.load(f)
except Exception as e:
    print(f"Error loading model from {MODEL_PATH}: {e}")
    svc_model = None

# Load CSV datasets
try:
    description_df = pd.read_csv(os.path.join(DATASETS_DIR, "symptom_Description.csv"))
    precautions_df = pd.read_csv(os.path.join(DATASETS_DIR, "symptom_precaution.csv"))
    medications_df = pd.read_csv(os.path.join(DATASETS_DIR, "medications.csv"))
    diets_df = pd.read_csv(os.path.join(DATASETS_DIR, "diets.csv"))
    workout_df = pd.read_csv(os.path.join(DATASETS_DIR, "workout_df.csv"))
except Exception as e:
    print(f"Error loading CSV datasets: {e}")
    description_df = pd.DataFrame()
    precautions_df = pd.DataFrame()
    medications_df = pd.DataFrame()
    diets_df = pd.DataFrame()
    workout_df = pd.DataFrame()

# 132 symptoms mapping dictionary
symptoms_dict = {
    'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4,
    'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9,
    'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14,
    'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19,
    'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24,
    'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29,
    'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34,
    'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39,
    'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44,
    'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48,
    'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52,
    'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57,
    'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61,
    'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66,
    'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71,
    'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75,
    'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79,
    'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84,
    'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88,
    'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92,
    'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96,
    'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100,
    'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104,
    'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108,
    'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111,
    'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115,
    'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118,
    'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122,
    'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126,
    'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130,
    'yellow_crust_ooze': 131
}

# 41 diseases target map
diseases_list = {
    15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction',
    33: 'Peptic ulcer disease', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma',
    23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)',
    28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A',
    19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis',
    36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)',
    18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia',
    31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne',
    38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'
}

def query_recommendations(disease_name):
    """
    Robust query for disease description, precautions, medications, diets, and workouts.
    Strips multiple contiguous whitespaces, leading/trailing spaces, and ignores capitalization.
    """
    clean_name = " ".join(disease_name.strip().split()).lower()

    # Description
    desc_matches = description_df[description_df['Disease'].str.strip().str.replace(r'\s+', ' ', regex=True).str.lower() == clean_name]
    desc = desc_matches['Description'].values[0] if not desc_matches.empty else "No description available for this condition."

    # Precautions
    prec_matches = precautions_df[precautions_df['Disease'].str.strip().str.replace(r'\s+', ' ', regex=True).str.lower() == clean_name]
    if not prec_matches.empty:
        cols = ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']
        prec = [str(val).strip() for val in prec_matches[cols].values[0] if pd.notna(val) and str(val).strip() != ""]
    else:
        prec = []

    # Medications
    med_matches = medications_df[medications_df['Disease'].str.strip().str.replace(r'\s+', ' ', regex=True).str.lower() == clean_name]
    meds = []
    if not med_matches.empty:
        raw_val = med_matches['Medication'].values[0]
        try:
            meds = ast.literal_eval(raw_val)
            meds = [m.strip() for m in meds]
        except Exception:
            meds = [r.strip() for r in raw_val.split(',') if r.strip() != ""]
    
    # Diets
    diet_matches = diets_df[diets_df['Disease'].str.strip().str.replace(r'\s+', ' ', regex=True).str.lower() == clean_name]
    diets = []
    if not diet_matches.empty:
        raw_val = diet_matches['Diet'].values[0]
        try:
            diets = ast.literal_eval(raw_val)
            diets = [d.strip() for d in diets]
        except Exception:
            diets = [r.strip() for r in raw_val.split(',') if r.strip() != ""]

    # Workouts
    workout_matches = workout_df[workout_df['disease'].str.strip().str.replace(r'\s+', ' ', regex=True).str.lower() == clean_name]
    workouts = []
    if not workout_matches.empty:
        workouts = [str(w).strip() for w in workout_matches['workout'].values if pd.notna(w) and str(w).strip() != ""]

    return desc, prec, meds, diets, workouts

@app.route("/")
def home():
    """Render the homepage dashboard."""
    return render_template("index.html")

@app.route("/api/symptoms", methods=["GET"])
def get_symptoms():
    """Return the list of all available symptoms for the frontend searchable dropdown."""
    # Return alphabetical list of symptoms
    sorted_symptoms = sorted(list(symptoms_dict.keys()))
    return jsonify(sorted_symptoms)

@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Accept user selected symptoms, calculate classification probabilities via SVC decision boundaries,
    rank top 3 differential diagnosis conditions, and fetch associated health report recommendations.
    """
    if svc_model is None:
        return jsonify({"error": "Machine learning model file 'svc.pkl' is not loaded."}), 500

    data = request.get_json() or {}
    user_symptoms = data.get("symptoms", [])

    if not user_symptoms:
        return jsonify({"error": "No symptoms provided. Please select at least one symptom."}), 400

    # Initialize 132-dimension feature vector
    input_vector = np.zeros(len(symptoms_dict))
    
    # Map valid symptoms
    mapped_count = 0
    for symptom in user_symptoms:
        symptom_clean = symptom.strip().lower()
        if symptom_clean in symptoms_dict:
            input_vector[symptoms_dict[symptom_clean]] = 1.0
            mapped_count += 1

    if mapped_count == 0:
        return jsonify({"error": "None of the provided symptoms are recognized by the classification model."}), 400

    try:
        # Perform inference on boundary scores
        decision_scores = svc_model.decision_function([input_vector])[0]
        
        # Apply Softmax to map decision values to relative probabilities
        e_x = np.exp(decision_scores - np.max(decision_scores))
        probabilities = e_x / e_x.sum()
        
        # Map scores to their disease categories
        ranked_results = []
        for class_idx, prob in enumerate(probabilities):
            disease = diseases_list.get(class_idx, "Unknown Condition")
            ranked_results.append({
                "disease": disease,
                "probability": round(float(prob) * 100, 1)
            })
        
        # Sort by probability in descending order and filter top 3 candidate conditions
        ranked_results = sorted(ranked_results, key=lambda x: x["probability"], reverse=True)
        top_results = ranked_results[:3]
        
        # Compile patient report parameters for all top 3 matches
        differential_diagnoses = []
        for res in top_results:
            dis_name = res["disease"]
            desc, precautions, medications, diets, workouts = query_recommendations(dis_name)
            
            differential_diagnoses.append({
                "disease": dis_name,
                "probability": res["probability"],
                "details": {
                    "description": desc,
                    "precautions": precautions,
                    "medications": medications,
                    "diets": diets,
                    "workouts": workouts
                }
            })
            
        return jsonify({
            "status": "success",
            "differential_diagnoses": differential_diagnoses
        })
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

import re

def extract_symptoms_from_text(text):
    """
    Lightweight keyword-based NLP: scans the user's natural language description
    and extracts matching symptoms from the known symptoms_dict.
    Handles underscores vs spaces, partial phrase matching, and common aliases.
    """
    # Normalise input: lowercase, remove punctuation noise
    text_lower = re.sub(r"[^\w\s]", " ", text.lower())
    text_lower = re.sub(r"\s+", " ", text_lower).strip()

    matched = []

    # Common aliases / layman terms → canonical symptom names
    aliases = {
        "fever": ["high_fever", "mild_fever"],
        "high fever": ["high_fever"],
        "mild fever": ["mild_fever"],
        "temperature": ["high_fever"],
        "runny nose": ["runny_nose"],
        "stuffy nose": ["congestion"],
        "blocked nose": ["congestion"],
        "sore throat": ["patches_in_throat", "throat_irritation"],
        "throat irritation": ["throat_irritation"],
        "stomach ache": ["stomach_pain", "abdominal_pain"],
        "belly pain": ["belly_pain", "abdominal_pain"],
        "tummy pain": ["abdominal_pain"],
        "chest pain": ["chest_pain"],
        "back pain": ["back_pain"],
        "neck pain": ["neck_pain"],
        "knee pain": ["knee_pain"],
        "hip pain": ["hip_joint_pain"],
        "joint pain": ["joint_pain"],
        "muscle pain": ["muscle_pain"],
        "muscle weakness": ["muscle_weakness"],
        "tired": ["fatigue", "lethargy"],
        "tiredness": ["fatigue"],
        "exhausted": ["fatigue"],
        "weakness": ["fatigue", "weakness_in_limbs"],
        "dizzy": ["dizziness"],
        "dizziness": ["dizziness"],
        "nausea": ["nausea"],
        "nauseous": ["nausea"],
        "vomit": ["vomiting"],
        "vomiting": ["vomiting"],
        "diarrhea": ["diarrhoea"],
        "diarrhoea": ["diarrhoea"],
        "loose stool": ["diarrhoea"],
        "itching": ["itching"],
        "itchy": ["itching"],
        "rash": ["skin_rash"],
        "skin rash": ["skin_rash"],
        "blister": ["blister"],
        "swelling": ["swelling_joints", "swelling_of_stomach"],
        "swollen": ["swelled_lymph_nodes", "swollen_legs"],
        "headache": ["headache"],
        "head pain": ["headache"],
        "migraine": ["headache"],
        "cough": ["cough"],
        "sneezing": ["continuous_sneezing"],
        "shortness of breath": ["breathlessness"],
        "breathless": ["breathlessness"],
        "difficulty breathing": ["breathlessness"],
        "chills": ["chills"],
        "shivering": ["shivering"],
        "sweating": ["sweating"],
        "night sweats": ["sweating"],
        "dehydration": ["dehydration"],
        "thirst": ["dehydration"],
        "weight loss": ["weight_loss"],
        "weight gain": ["weight_gain"],
        "anxiety": ["anxiety"],
        "depression": ["depression"],
        "irritability": ["irritability"],
        "mood swings": ["mood_swings"],
        "constipation": ["constipation"],
        "indigestion": ["indigestion"],
        "acidity": ["acidity"],
        "heartburn": ["acidity"],
        "loss of appetite": ["loss_of_appetite"],
        "no appetite": ["loss_of_appetite"],
        "increased appetite": ["increased_appetite"],
        "yellowing": ["yellowing_of_eyes", "yellowish_skin"],
        "jaundice": ["yellowish_skin", "yellowing_of_eyes"],
        "yellow eyes": ["yellowing_of_eyes"],
        "yellow skin": ["yellowish_skin"],
        "dark urine": ["dark_urine"],
        "blood in urine": ["burning_micturition"],
        "painful urination": ["burning_micturition"],
        "frequent urination": ["continuous_feel_of_urine", "polyuria"],
        "blurred vision": ["blurred_and_distorted_vision"],
        "vision problem": ["blurred_and_distorted_vision", "visual_disturbances"],
        "red eyes": ["redness_of_eyes"],
        "watery eyes": ["watering_from_eyes"],
        "palpitations": ["palpitations"],
        "fast heartbeat": ["fast_heart_rate"],
        "rapid heart": ["fast_heart_rate"],
        "stiff neck": ["stiff_neck"],
        "obesity": ["obesity"],
        "acne": ["pus_filled_pimples", "blackheads"],
        "pimples": ["pus_filled_pimples"],
    }

    # 1. Check aliases first
    for alias, targets in aliases.items():
        if alias in text_lower:
            for t in targets:
                if t in symptoms_dict and t not in matched:
                    matched.append(t)

    # 2. Direct symptom name matching (underscores replaced with spaces)
    for symptom in symptoms_dict:
        symptom_readable = symptom.replace("_", " ").strip()
        if symptom_readable in text_lower and symptom not in matched:
            matched.append(symptom)

    # 3. Single-word token matching for remaining unmatched symptoms
    tokens = set(text_lower.split())
    for symptom in symptoms_dict:
        if symptom in matched:
            continue
        parts = [p for p in re.split(r"[_\s]+", symptom) if len(p) > 3]
        if parts and all(p in tokens for p in parts):
            matched.append(symptom)

    return matched


@app.route("/api/predict_nlp", methods=["POST"])
def predict_nlp():
    """
    Accept natural language symptom descriptions, extract symptoms via keyword NLP,
    run the SVC model and return top 3 differential diagnoses with health reports.
    No heavy ML libraries required — uses the same SVC model as the checklist mode.
    """
    if svc_model is None:
        return jsonify({"error": "Machine learning model file 'svc.pkl' is not loaded."}), 500

    data = request.get_json() or {}
    narrative = data.get("description", "").strip()

    if not narrative or len(narrative) < 10:
        return jsonify({"error": "Symptom description is too short. Please describe in detail (minimum 10 characters)."}), 400

    # Extract symptoms from free text
    matched_symptoms = extract_symptoms_from_text(narrative)

    if not matched_symptoms:
        return jsonify({
            "error": "No recognisable symptoms were found in your description. "
                     "Try including specific terms like 'headache', 'fever', 'nausea', 'chest pain', etc."
        }), 400

    # Build feature vector and run SVC — same as checklist mode
    input_vector = np.zeros(len(symptoms_dict))
    for symptom in matched_symptoms:
        input_vector[symptoms_dict[symptom]] = 1.0

    try:
        decision_scores = svc_model.decision_function([input_vector])[0]
        e_x = np.exp(decision_scores - np.max(decision_scores))
        probabilities = e_x / e_x.sum()

        ranked_results = []
        for class_idx, prob in enumerate(probabilities):
            disease = diseases_list.get(class_idx, "Unknown Condition")
            ranked_results.append({"disease": disease, "probability": round(float(prob) * 100, 1)})

        ranked_results = sorted(ranked_results, key=lambda x: x["probability"], reverse=True)
        top_results = ranked_results[:3]

        differential_diagnoses = []
        for res in top_results:
            dis_name = res["disease"]
            desc, precautions, medications, diets, workouts = query_recommendations(dis_name)
            differential_diagnoses.append({
                "disease": dis_name,
                "probability": res["probability"],
                "details": {
                    "description": desc,
                    "precautions": precautions,
                    "medications": medications,
                    "diets": diets,
                    "workouts": workouts
                }
            })

        return jsonify({
            "status": "success",
            "matched_symptoms": matched_symptoms,
            "differential_diagnoses": differential_diagnoses
        })
    except Exception as e:
        return jsonify({"error": f"NLP diagnostics failed: {str(e)}"}), 500

# ── BigQuery Live Health Intelligence ──────────────────────────────────────
# Path to GCP service account credentials JSON
GCP_CREDENTIALS_PATH = os.path.join("credentials", "gcp_credentials.json")
GCP_PROJECT_ID = None  # Will be read from credentials file automatically

# ── Static Demo Data (shown when BigQuery credentials are not configured) ──
# Sources: WHO Global Health Observatory, World Bank, CDC — approximate figures
DISEASE_DEMO_DATA = {
    "_default": {
        "covid_data": {
            "source": "WHO Global Health Observatory (Demo Data)",
            "global_total": 704_753_890,
            "global_new_30d": 1_240_000,
            "top_countries": [
                {"country": "United States", "total": 103_436_829, "new_7d": 42000, "date": "2024-01-01"},
                {"country": "China",         "total": 99_256_470,  "new_7d": 31000, "date": "2024-01-01"},
                {"country": "India",         "total": 44_694_106,  "new_7d": 8500,  "date": "2024-01-01"},
                {"country": "France",        "total": 38_997_490,  "new_7d": 12000, "date": "2024-01-01"},
                {"country": "Germany",       "total": 38_437_756,  "new_7d": 9800,  "date": "2024-01-01"},
            ],
            "note": "Global respiratory / infectious disease burden data (WHO)"
        },
        "world_bank_data": {
            "source": "World Bank Health & Population (Demo Data)",
            "country": "India",
            "indicators": [
                {"indicator": "Life expectancy at birth, total (years)", "value": 70.19, "year": 2021},
                {"indicator": "Physicians (per 1,000 people)",            "value": 0.74,  "year": 2020},
                {"indicator": "Hospital beds (per 1,000 people)",         "value": 0.5,   "year": 2017},
            ]
        }
    },
    "diabetes": {
        "covid_data": {
            "source": "IDF Diabetes Atlas 10th Edition (Demo Data)",
            "global_total": 537_000_000,
            "global_new_30d": 4_100_000,
            "top_countries": [
                {"country": "China",         "total": 140_870_000, "new_7d": 950000, "date": "2023-01-01"},
                {"country": "India",         "total": 101_000_000, "new_7d": 720000, "date": "2023-01-01"},
                {"country": "United States", "total": 37_300_000,  "new_7d": 210000, "date": "2023-01-01"},
                {"country": "Pakistan",      "total": 33_000_000,  "new_7d": 180000, "date": "2023-01-01"},
                {"country": "Brazil",        "total": 15_700_000,  "new_7d": 95000,  "date": "2023-01-01"},
            ],
            "note": "Global Diabetes prevalence — IDF Atlas 2021"
        },
        "world_bank_data": {
            "source": "World Bank Health & Population (Demo Data)",
            "country": "India",
            "indicators": [
                {"indicator": "Life expectancy at birth, total (years)", "value": 70.19, "year": 2021},
                {"indicator": "Physicians (per 1,000 people)",            "value": 0.74,  "year": 2020},
                {"indicator": "Hospital beds (per 1,000 people)",         "value": 0.5,   "year": 2017},
            ]
        }
    },
    "hypertension": {
        "covid_data": {
            "source": "WHO Hypertension Global Report (Demo Data)",
            "global_total": 1_280_000_000,
            "global_new_30d": 10_500_000,
            "top_countries": [
                {"country": "China",         "total": 254_000_000, "new_7d": 1900000, "date": "2023-01-01"},
                {"country": "India",         "total": 188_300_000, "new_7d": 1600000, "date": "2023-01-01"},
                {"country": "United States", "total": 108_200_000, "new_7d": 750000,  "date": "2023-01-01"},
                {"country": "Russia",        "total": 44_000_000,  "new_7d": 310000,  "date": "2023-01-01"},
                {"country": "Indonesia",     "total": 63_400_000,  "new_7d": 440000,  "date": "2023-01-01"},
            ],
            "note": "Global Hypertension prevalence — WHO 2023"
        },
        "world_bank_data": {
            "source": "World Bank Health & Population (Demo Data)",
            "country": "India",
            "indicators": [
                {"indicator": "Life expectancy at birth, total (years)", "value": 70.19, "year": 2021},
                {"indicator": "Physicians (per 1,000 people)",            "value": 0.74,  "year": 2020},
                {"indicator": "Hospital beds (per 1,000 people)",         "value": 0.5,   "year": 2017},
            ]
        }
    },
    "tuberculosis": {
        "covid_data": {
            "source": "WHO Global TB Report 2023 (Demo Data)",
            "global_total": 10_600_000,
            "global_new_30d": 883_000,
            "top_countries": [
                {"country": "India",         "total": 2_820_000, "new_7d": 235000, "date": "2023-01-01"},
                {"country": "Indonesia",     "total": 1_060_000, "new_7d": 88300,  "date": "2023-01-01"},
                {"country": "China",         "total": 748_000,   "new_7d": 62300,  "date": "2023-01-01"},
                {"country": "Philippines",   "total": 800_000,   "new_7d": 66700,  "date": "2023-01-01"},
                {"country": "Pakistan",      "total": 611_000,   "new_7d": 50900,  "date": "2023-01-01"},
            ],
            "note": "Global TB incidence — WHO Global Tuberculosis Report 2023"
        },
        "world_bank_data": {
            "source": "World Bank Health & Population (Demo Data)",
            "country": "India",
            "indicators": [
                {"indicator": "Life expectancy at birth, total (years)", "value": 70.19, "year": 2021},
                {"indicator": "Physicians (per 1,000 people)",            "value": 0.74,  "year": 2020},
                {"indicator": "Hospital beds (per 1,000 people)",         "value": 0.5,   "year": 2017},
            ]
        }
    },
    "malaria": {
        "covid_data": {
            "source": "WHO World Malaria Report 2023 (Demo Data)",
            "global_total": 249_000_000,
            "global_new_30d": 20_750_000,
            "top_countries": [
                {"country": "Nigeria",        "total": 68_180_000, "new_7d": 5680000, "date": "2023-01-01"},
                {"country": "DR Congo",       "total": 30_140_000, "new_7d": 2510000, "date": "2023-01-01"},
                {"country": "Uganda",         "total": 13_220_000, "new_7d": 1100000, "date": "2023-01-01"},
                {"country": "Mozambique",     "total": 11_470_000, "new_7d": 955000,  "date": "2023-01-01"},
                {"country": "India",          "total": 5_490_000,  "new_7d": 457000,  "date": "2023-01-01"},
            ],
            "note": "Global Malaria cases — WHO World Malaria Report 2023"
        },
        "world_bank_data": {
            "source": "World Bank Health & Population (Demo Data)",
            "country": "India",
            "indicators": [
                {"indicator": "Life expectancy at birth, total (years)", "value": 70.19, "year": 2021},
                {"indicator": "Physicians (per 1,000 people)",            "value": 0.74,  "year": 2020},
                {"indicator": "Hospital beds (per 1,000 people)",         "value": 0.5,   "year": 2017},
            ]
        }
    },
    "dengue": {
        "covid_data": {
            "source": "WHO Dengue Global Situation (Demo Data)",
            "global_total": 390_000_000,
            "global_new_30d": 32_500_000,
            "top_countries": [
                {"country": "India",         "total": 85_000_000, "new_7d": 7080000, "date": "2023-01-01"},
                {"country": "Brazil",        "total": 61_000_000, "new_7d": 5080000, "date": "2023-01-01"},
                {"country": "Indonesia",     "total": 51_000_000, "new_7d": 4250000, "date": "2023-01-01"},
                {"country": "Philippines",   "total": 28_000_000, "new_7d": 2330000, "date": "2023-01-01"},
                {"country": "Bangladesh",    "total": 18_000_000, "new_7d": 1500000, "date": "2023-01-01"},
            ],
            "note": "Global Dengue infections — WHO / Bhatt et al. 2023"
        },
        "world_bank_data": {
            "source": "World Bank Health & Population (Demo Data)",
            "country": "India",
            "indicators": [
                {"indicator": "Life expectancy at birth, total (years)", "value": 70.19, "year": 2021},
                {"indicator": "Physicians (per 1,000 people)",            "value": 0.74,  "year": 2020},
                {"indicator": "Hospital beds (per 1,000 people)",         "value": 0.5,   "year": 2017},
            ]
        }
    },
    "pneumonia": {
        "covid_data": {
            "source": "WHO Pneumonia Statistics (Demo Data)",
            "global_total": 450_000_000,
            "global_new_30d": 37_500_000,
            "top_countries": [
                {"country": "India",         "total": 127_000_000, "new_7d": 10580000, "date": "2023-01-01"},
                {"country": "China",         "total": 88_000_000,  "new_7d": 7330000,  "date": "2023-01-01"},
                {"country": "Nigeria",       "total": 43_000_000,  "new_7d": 3580000,  "date": "2023-01-01"},
                {"country": "Pakistan",      "total": 22_000_000,  "new_7d": 1830000,  "date": "2023-01-01"},
                {"country": "Bangladesh",    "total": 18_000_000,  "new_7d": 1500000,  "date": "2023-01-01"},
            ],
            "note": "Global Pneumonia cases — WHO Global Health Estimates 2023"
        },
        "world_bank_data": {
            "source": "World Bank Health & Population (Demo Data)",
            "country": "India",
            "indicators": [
                {"indicator": "Life expectancy at birth, total (years)", "value": 70.19, "year": 2021},
                {"indicator": "Physicians (per 1,000 people)",            "value": 0.74,  "year": 2020},
                {"indicator": "Hospital beds (per 1,000 people)",         "value": 0.5,   "year": 2017},
            ]
        }
    },
    "heart attack": {
        "covid_data": {
            "source": "WHO Cardiovascular Disease Statistics (Demo Data)",
            "global_total": 523_000_000,
            "global_new_30d": 43_600_000,
            "top_countries": [
                {"country": "China",         "total": 112_000_000, "new_7d": 9330000, "date": "2023-01-01"},
                {"country": "India",         "total": 64_000_000,  "new_7d": 5330000, "date": "2023-01-01"},
                {"country": "United States", "total": 37_000_000,  "new_7d": 3080000, "date": "2023-01-01"},
                {"country": "Russia",        "total": 24_000_000,  "new_7d": 2000000, "date": "2023-01-01"},
                {"country": "Brazil",        "total": 19_000_000,  "new_7d": 1580000, "date": "2023-01-01"},
            ],
            "note": "Global Cardiovascular Disease prevalence — WHO 2023"
        },
        "world_bank_data": {
            "source": "World Bank Health & Population (Demo Data)",
            "country": "India",
            "indicators": [
                {"indicator": "Life expectancy at birth, total (years)", "value": 70.19, "year": 2021},
                {"indicator": "Physicians (per 1,000 people)",            "value": 0.74,  "year": 2020},
                {"indicator": "Hospital beds (per 1,000 people)",         "value": 0.5,   "year": 2017},
            ]
        }
    },
}

def get_demo_data(disease_name: str) -> dict:
    """Return demo health data for a given disease name, falling back to _default."""
    key = disease_name.lower().strip()
    # Try exact match, then partial match
    if key in DISEASE_DEMO_DATA:
        return DISEASE_DEMO_DATA[key]
    for k in DISEASE_DEMO_DATA:
        if k != "_default" and (k in key or key in k):
            return DISEASE_DEMO_DATA[k]
    return DISEASE_DEMO_DATA["_default"]

def get_bq_client():
    """Return a BigQuery client using service account credentials if available."""
    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account

        if not os.path.exists(GCP_CREDENTIALS_PATH):
            return None, "credentials_missing"

        creds = service_account.Credentials.from_service_account_file(
            GCP_CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/bigquery.readonly"]
        )
        project_id = creds.project_id
        client = bigquery.Client(credentials=creds, project=project_id)
        return client, "ok"
    except ImportError:
        return None, "library_not_installed"
    except Exception as e:
        return None, str(e)


def query_covid19_stats(client, disease_name):
    """
    Query Google's public COVID-19 open dataset for global case stats.
    Returns aggregated totals and top affected countries.
    """
    from google.cloud import bigquery

    # Use confirmed_cases as a proxy for disease burden
    query = """
        SELECT
            country_name,
            SUM(new_confirmed) AS new_cases_7d,
            SUM(cumulative_confirmed) AS total_confirmed,
            MAX(date) AS latest_date
        FROM `bigquery-public-data.covid19_open_data.covid19_open_data`
        WHERE
            date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            AND aggregation_level = 0
            AND cumulative_confirmed > 0
        GROUP BY country_name
        ORDER BY total_confirmed DESC
        LIMIT 10
    """
    job = client.query(query)
    rows = list(job.result())

    countries = []
    global_total = 0
    global_new_7d = 0
    for row in rows:
        countries.append({
            "country": row.country_name,
            "total": int(row.total_confirmed or 0),
            "new_7d": int(row.new_cases_7d or 0),
            "date": str(row.latest_date)
        })
        global_total += int(row.total_confirmed or 0)
        global_new_7d += int(row.new_cases_7d or 0)

    return {
        "source": "Google BigQuery — COVID-19 Open Data",
        "global_total": global_total,
        "global_new_30d": global_new_7d,
        "top_countries": countries[:5],
        "note": f"Showing global COVID-19 data as a disease-burden proxy for '{disease_name}'"
    }


def query_world_bank_health(client, disease_name):
    """
    Query World Bank public health & population dataset for health indicators.
    """
    query = """
        SELECT
            country_name,
            indicator_name,
            ROUND(value, 2) AS value,
            year
        FROM `bigquery-public-data.world_bank_health_population.health_nutrition_population`
        WHERE
            indicator_name IN (
                'Life expectancy at birth, total (years)',
                'Physicians (per 1,000 people)',
                'Hospital beds (per 1,000 people)'
            )
            AND year = (
                SELECT MAX(year)
                FROM `bigquery-public-data.world_bank_health_population.health_nutrition_population`
                WHERE country_name = 'India'
            )
            AND country_name = 'India'
        ORDER BY indicator_name
    """
    job = client.query(query)
    rows = list(job.result())

    indicators = []
    for row in rows:
        indicators.append({
            "indicator": row.indicator_name,
            "value": float(row.value) if row.value else None,
            "year": int(row.year)
        })

    return {
        "source": "Google BigQuery — World Bank Health Data",
        "country": "India",
        "indicators": indicators
    }


@app.route("/api/health_intelligence/<path:disease_name>", methods=["GET"])
def health_intelligence(disease_name):
    """
    Fetch live health statistics from Google BigQuery public datasets.
    Falls back to curated WHO/IDF/World Bank static data when BigQuery
    credentials are not configured — so the panel always shows data.
    """
    client, status = get_bq_client()

    # ── Fallback: serve curated static data when no credentials available ──
    if status in ("credentials_missing", "library_not_installed") or client is None:
        demo = get_demo_data(disease_name)
        demo_covid = demo["covid_data"].copy()
        demo_wb    = demo["world_bank_data"].copy()

        # Tag the source so frontend can show a "Demo" badge
        demo_covid["demo"] = True
        demo_wb["demo"]    = True

        return jsonify({
            "status": "ok",
            "demo":   True,   # frontend uses this to show "(Reference Data)" label
            "disease": disease_name,
            "covid_data":      demo_covid,
            "world_bank_data": demo_wb
        }), 200

    # ── Live BigQuery path ────────────────────────────────────────────────
    try:
        covid_stats = query_covid19_stats(client, disease_name)
        wb_stats    = query_world_bank_health(client, disease_name)

        return jsonify({
            "status": "ok",
            "demo":   False,
            "disease": disease_name,
            "covid_data":      covid_stats,
            "world_bank_data": wb_stats
        })
    except Exception as e:
        # Even on BigQuery error, fall back to demo data
        demo = get_demo_data(disease_name)
        demo["covid_data"]["demo"] = True
        demo["world_bank_data"]["demo"] = True
        return jsonify({
            "status": "ok",
            "demo":   True,
            "disease": disease_name,
            "bq_error": str(e),
            "covid_data":      demo["covid_data"],
            "world_bank_data": demo["world_bank_data"]
        }), 200



if __name__ == "__main__":
    # Get port from environment (Hugging Face / Render set this) or fallback to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=port)

