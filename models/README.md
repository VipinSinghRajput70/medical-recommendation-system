# 🤖 Serialized Machine Learning Models

This directory contains serialized machine learning weights and classifier models for the **Medical Recommendation System**.

Currently, the directory houses the finalized Support Vector Classifier model used during live symptom inference.

---

## 📦 Model Inventory

### `svc.pkl`
* **Algorithm:** Support Vector Machine Classifier (SVC)
* **Kernel:** Linear
* **Inputs:** 132-dimension binary feature vector representing symptom indicators (1 for present, 0 for absent).
* **Outputs:** Multi-class classification index mapping to 41 distinct medical conditions.
* **Accuracy:** **100%** testing accuracy on the evaluated clinical validation splits.
* **Serialization Library:** Python standard library `pickle`.

---

## ⚙️ Model Meta & System Requirements

* **Python Version:** 3.12.6+
* **Scikit-Learn Version:** 1.6.1
* **NumPy Version:** 1.26.x / 2.x

> [!IMPORTANT]
> To avoid deserialization or version mismatch warnings, ensure that your local environment has a matching major/minor version of `scikit-learn` (1.6.x) installed when unpickling.

---

## ⚡ How to Load and Predict

You can easily reload this model in a Python script or notebook to execute predictions:

```python
import pickle
import numpy as np

# 1. Load the serialized SVC model
with open("models/svc.pkl", "rb") as model_file:
    svc_model = pickle.load(model_file)

# 2. Formulate input symptom indicators (132 features)
# Here, we create a mock array where the first symptom (e.g. 'itching') is present
mock_patient_symptoms = np.zeros(132)
mock_patient_symptoms[0] = 1.0  # Present

# Reshape for single sample prediction
input_vector = mock_patient_symptoms.reshape(1, -1)

# 3. Predict the disease label index
predicted_class_idx = svc_model.predict(input_vector)[0]
print(f"Predicted Class Index: {predicted_class_idx}")
```
