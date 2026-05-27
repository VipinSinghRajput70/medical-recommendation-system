# 📊 Relational Healthcare Datasets

This directory contains the supporting CSV datasets used by the **Medical Recommendation System** to retrieve recommendations, diets, exercise plans, medications, and disease descriptions.

All datasets are structured with relational linkage to the predicted disease name (the prognosis outcome).

---

## 📂 File Registry & Descriptions

### 1. `description.csv`
Contains the diagnostic descriptions of various diseases.
* **Columns:**
  * `Disease`: The official name of the disease (acts as the primary lookup key).
  * `Description`: A concise, patient-friendly summary describing the pathology of the disease.

### 2. `precautions_df.csv`
Provides a multi-step checklist of preventative actions to manage each condition.
* **Columns:**
  * `Disease`: The name of the disease.
  * `Precaution_1`, `Precaution_2`, `Precaution_3`, `Precaution_4`: Ordered sequential actions recommended to reduce symptoms or avoid complications.

### 3. `medications.csv`
Lists typical medical treatments or pharmaceutical remedies.
* **Columns:**
  * `Disease`: The name of the disease.
  * `Medication`: Recommended medications or active chemical compounds (formatted as a list structure).

### 4. `diets.csv`
Provides customized dietary guidelines for nutritional support.
* **Columns:**
  * `Disease`: The name of the disease.
  * `Diet`: Tailored foods, drinks, or nutritional items to consume/avoid.

### 5. `workout_df.csv`
Supplies physiotherapeutic exercise or workout advice.
* **Columns:**
  * `disease`: The name of the disease (lowercase header).
  * `workout`: Specific physical training recommendations, cardiovascular workouts, or active rest programs.

### 6. `symtoms_df.csv`
A lookup dataset mapping symptoms to their severity and relative categorization codes.

---

## 🛠️ Data Loading Example (Python)

These CSVs can be quickly loaded into a pandas DataFrame using the following snippet:

```python
import pandas as pd

# Load datasets
description_df = pd.read_csv("datasets/description.csv")
precautions_df = pd.read_csv("datasets/precautions_df.csv")
medications_df = pd.read_csv("datasets/medications.csv")
diets_df       = pd.read_csv("datasets/diets.csv")
workout_df     = pd.read_csv("datasets/workout_df.csv")

# Retrieve information for a predicted disease
disease_name = "Diabetes "
disease_desc = description_df[description_df['Disease'] == disease_name]['Description'].values[0]
print(f"Description for {disease_name}: {disease_desc}")
```
