
def get_default_values(disease_type):
    """
    Returns median/default values for imputation if fields are missing.
    Based on PIMA (Diabetes) and UCI (Heart) dataset statistics.
    """
    if disease_type == "diabetes":
        return {
            "pregnancies": 3,
            "glucose": 120,
            "bloodpressure": 72,
            "skinthickness": 23,
            "insulin": 30, # PIMA median is low, but clincal norm is different. Using dataset median approx.
            "bmi": 32.0,
            "diabetespedigreefunction": 0.37,
            "age": 29
        }
    elif disease_type == "heart":
        return {
            "age": 55,
            "sex": 1,
            "cp": 0,       # Asymptomatic
            "trestbps": 130,
            "chol": 240,
            "fbs": 0,      # < 120 mg/dl
            "restecg": 1,  # Normal
            "thalach": 153,
            "exang": 0,    # No
            "oldpeak": 0.8,
            "slope": 1,
            "ca": 0,
            "thal": 2      # Normal
        }
    return {}

def calculate_risk_level(prob_percentage):
    """
    Maps probability percentage to a Risk Level.
    """
    if prob_percentage < 40:
        return "Low"
    elif prob_percentage < 75:
        return "Moderate"
    else:
        return "High"

def get_clinical_summary(disease_type, data, risk_level):
    """
    Generates a simple clinical summary based on key parameters.
    """
    summary = []
    
    if disease_type == "diabetes":
        gluc = float(data.get("glucose", 0))
        bmi = float(data.get("bmi", 0))
        
        if gluc > 140:
            summary.append(f"Elevated Glucose ({gluc} mg/dL)")
        if bmi > 30:
            summary.append(f"Obesity indicated (BMI {bmi})")
            
    elif disease_type == "heart":
        chol = float(data.get("chol", 0))
        bp = float(data.get("trestbps", 0))
        
        if chol > 240:
            summary.append(f"High Cholesterol ({chol} mg/dL)")
        if bp > 140:
            summary.append(f"Hypertension ({bp} mmHg)")
            
    if not summary:
        return f"Patient shows {risk_level} risk profile based on provided parameters."
    
    return f"Patient shows {risk_level} risk. Key concerns: " + ", ".join(summary) + "."
