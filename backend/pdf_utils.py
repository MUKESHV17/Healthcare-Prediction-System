import re
from pypdf import PdfReader

def extract_data_from_pdf(file_path):
    """
    Extracts clinical data from a PDF report using regex patterns.
    Returns a dictionary of found parameters.
    """
    data = {}
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Normalize text
        text = text.lower()
        
        # Define Regex Patterns for Clinical Parameters
        patterns = {
            # Common
            "name": r"(?:patient\s*name|name)\s*[:\-]?\s*([a-z\s\.]+)(?=\n|age|sex|$)",
            "age": r"age\s*(?:/\s*sex)?\s*[:\-]?\s*(\d{2})",
            "sex": r"sex\s*[:\-]?\s*(male|female|m|f)",
            
            # Diabetes
            "glucose": r"glucose\s*(?:\(.*\))?\s*[:\-]?\s*(\d{2,3})",
            "blood_pressure": r"blood pressure\s*(?:\(.*\))?\s*[:\-]?\s*(\d{2,3}/\d{2,3})",
            "bp": r"bp\s*(?:\(.*\))?\s*[:\-]?\s*(\d{2,3}/\d{2,3})",
            "pregnancies": r"pregnancies\s*(?:\(.*\))?\s*[:\-]?\s*(\d+)",
            "insulin": r"insulin\s*(?:\(.*\))?\s*[:\-]?\s*(\d{2,3})",
            "bmi": r"bmi\s*(?:\(.*\))?\s*[:\-]?\s*(\d{2}(\.\d{1,2})?)",
            "skin_thickness": r"skin thickness\s*(?:\(.*\))?\s*[:\-]?\s*(\d{2,3})",
            "dpf": r"diabetes pedigree function\s*(?:\(.*\))?\s*[:\-]?\s*(\d+(\.\d+)?)",

            # Heart
            "cholesterol": r"(?:serum\s*)?cholesterol\s*(?:\(.*\))?\s*[:\-]?\s*(\d{2,3})",
            "trestbps": r"resting blood pressure\s*(?:\(.*\))?\s*[:\-]?\s*(\d{2,3})", 
            "thalach": r"max heart rate\s*(?:\(.*\))?\s*[:\-]?\s*(\d{2,3})",
            "oldpeak": r"st depression\s*(?:\(.*\))?\s*[:\-]?\s*(\d+(\.\d+)?)",
            "cp": r"chest pain type\s*(?:\(.*\))?\s*[:\-]?\s*(\d)",
            "ca": r"(?:number of )?major vessels\s*(?:blocked)?\s*(?:\(.*\))?\s*[:\-]?\s*(\d)",
            "thal": r"thalassemia\s*(?:\(.*\))?\s*[:\-]?\s*(normal|fixed|reversible|reversable|\d)",
            "exang": r"(?:exercise induced )?angina\s*(?:\(.*\))?\s*[:\-]?\s*(yes|no|1|0)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                
                # Handle Name extraction
                if key == "name":
                    data["name"] = value.strip().title()
                # Handle BP special case (split into syst/diast optional or just keep string)
                elif key == "blood_pressure" or key == "bp":
                    # Just store as string "120/80" for now, app.py will parse
                    data["blood_pressure"] = value
                elif key == "sex":
                    data["sex"] = 1 if value.startswith("m") else 0
                elif key == "thal":
                    if "reversible" in value or "reversable" in value:
                        data["thal"] = 3
                    elif "fixed" in value:
                        data["thal"] = 2
                    elif "normal" in value:
                        data["thal"] = 1
                    else:
                        try: data["thal"] = int(value)
                        except: pass
                elif key == "exang":
                    if "yes" in value:
                        data["exang"] = 1
                    elif "no" in value:
                        data["exang"] = 0
                    else:
                        try: data["exang"] = int(value)
                        except: pass
                else:
                    try:
                        # Try converting to float/int
                        if "." in value:
                            data[key] = float(value)
                        else:
                            data[key] = int(value)
                    except:
                        data[key] = value

        print(f"📄 Extracted Data from PDF: {data}")
        return data

    except Exception as e:
        print(f"❌ Error extracting PDF data: {e}")
        return {}
