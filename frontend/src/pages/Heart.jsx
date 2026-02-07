import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import HealthCharts from "../components/HealthCharts";
import { HelpCircle } from "lucide-react";
import "./Heart.css";

const HEART_METRICS_INFO = {
  age: {
    label: "Age",
    info: "Patient age in years.",
    range: "Normal: Any value. Risk increases significantly after 45 (men) and after 55 (women).",
    type: "number",
    placeholder: "Enter age"
  },
  sex: {
    label: "Sex",
    info: "Biological sex.",
    range: "1 = Male, 0 = Female. Males generally have higher early risk.",
    type: "select",
    options: [
      { label: "Male", value: "1" },
      { label: "Female", value: "0" }
    ]
  },
  cp: {
    label: "Chest Pain Type",
    info: "Type of chest pain experienced.",
    range: "Typical Angina (0) is high risk. Asymptomatic (3) or Non-anginal (2) are usually lower risk.",
    type: "select",
    options: [
      { label: "Typical Angina", value: "0" },
      { label: "Atypical Angina", value: "1" },
      { label: "Non-anginal Pain", value: "2" },
      { label: "Asymptomatic", value: "3" }
    ]
  },
  trestbps: {
    label: "Resting Blood Pressure",
    info: "Blood pressure at rest (mmHg).",
    range: "Normal: 90 – 120. High risk: > 140.",
    type: "number",
    placeholder: "Enter mmHg"
  },
  chol: {
    label: "Serum Cholesterol",
    info: "Cholesterol level (mg/dL).",
    range: "Normal: < 200, Borderline: 200–239, High: ≥ 240.",
    type: "number",
    placeholder: "Enter mg/dL"
  },
  fbs: {
    label: "Fasting Blood Sugar",
    info: "Blood sugar after fasting.",
    range: "Normal: ≤ 120 mg/dL (0), High: > 120 mg/dL (1).",
    type: "select",
    options: [
      { label: "Normal (≤ 120 mg/dL)", value: "0" },
      { label: "High (> 120 mg/dL)", value: "1" }
    ]
  },
  restecg: {
    label: "Resting ECG Result",
    info: "ECG reading at rest.",
    range: "Normal (0) is healthy. Abnormalities (1, 2) may indicate heart strain.",
    type: "select",
    options: [
      { label: "Normal", value: "0" },
      { label: "ST-T Wave Abnormality", value: "1" },
      { label: "Left Ventricular Hypertrophy", value: "2" }
    ]
  },
  thalach: {
    label: "Max Heart Rate",
    info: "Maximum heart rate achieved during exercise (bpm).",
    range: "Expected max: 220 - age. Significantly lower values can mean higher risk.",
    type: "number",
    placeholder: "Enter max bpm"
  },
  exang: {
    label: "Exercise Angina",
    info: "Chest pain during exercise.",
    range: "0 = No, 1 = Yes (High risk).",
    type: "select",
    options: [
      { label: "No", value: "0" },
      { label: "Yes", value: "1" }
    ]
  },
  oldpeak: {
    label: "ST Depression",
    info: "ECG ST depression during exercise.",
    range: "Normal: 0-1, Mild: 1-2, High risk: > 2.",
    type: "number",
    placeholder: "Enter depression value (e.g. 1.5)"
  },
  slope: {
    label: "ST Segment Slope",
    info: "Slope of the peak exercise ST segment.",
    range: "Upsloping (0) is Normal. Downsloping (2) is High risk.",
    type: "select",
    options: [
      { label: "Upsloping", value: "0" },
      { label: "Flat", value: "1" },
      { label: "Downsloping", value: "2" }
    ]
  },
  ca: {
    label: "Major Vessels Blocked",
    info: "Number of major vessels (0-3) with blockage.",
    range: "Normal: 0. High risk: ≥ 2.",
    type: "number",
    placeholder: "0 - 3"
  },
  thal: {
    label: "Thalassemia Status",
    info: "Blood flow status in the heart.",
    range: "Normal (1), Fixed defect (2), Reversible defect (3, High risk).",
    type: "select",
    options: [
      { label: "Normal", value: "1" },
      { label: "Fixed Defect", value: "2" },
      { label: "Reversible Defect", value: "3" }
    ]
  }
};

function Heart() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    age: "",
    sex: "",
    cp: "",
    trestbps: "",
    chol: "",
    fbs: "",
    restecg: "",
    thalach: "",
    exang: "",
    oldpeak: "",
    slope: "",
    ca: "",
    thal: ""
  });
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [gender, setGender] = useState("");
  const [activeTooltip, setActiveTooltip] = useState(null);

  useEffect(() => {
    const email = localStorage.getItem("email");
    if (email) {
      fetch(`http://127.0.0.1:5001/api/user/profile?email=${email}`)
        .then((res) => res.json())
        .then((data) => {
          if (!data.error) {
            setFormData((prev) => ({
              ...prev,
              age: data.age || prev.age,
              sex: String(data.gender).toLowerCase() === "male" ? "1" : String(data.gender).toLowerCase() === "female" ? "0" : prev.sex,
            }));
            setGender(data.gender);
          }
        })
        .catch((err) => console.error("Failed to load profile for pre-fill", err));
    }
  }, []);


  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    const data = new FormData();
    if (file) {
      data.append("file", file);
    }

    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });

    const email = localStorage.getItem("email");
    if (email) data.append("email", email);

    try {
      const response = await fetch("http://127.0.0.1:5001/predict/heart", {
        method: "POST",
        body: data
      });

      const resData = await response.json();
      setResult(resData);

      // Auto-send Report Email
      const userEmail = localStorage.getItem("email");
      if (userEmail && resData) {
        console.log("Triggering auto-email...");
        fetch("http://127.0.0.1:5001/generate_report", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            patient_data: resData.input_details,
            prediction: resData.prediction,
            risk_level: resData.risk_level,
            clinical_summary: resData.clinical_summary,
            disease_type: "heart",
            email: userEmail,
            patient_name: resData.patient_name,
            gender: resData.patient_sex || gender
          })
        }).then(res => {
          if (res.ok) console.log("Auto-email sent successfully");
        }).catch(err => console.error("Auto-email failed", err));
      }

    } catch (err) {
      console.error("Error predicting:", err);
    }
  };


  return (
    <div className="heart-container" onClick={() => setActiveTooltip(null)}>
      <Sidebar />

      <div className="heart-main">
        <div className="heart-card" style={{ maxWidth: result ? "900px" : "500px", transition: "all 0.3s" }}>
          <h2>Cardiovascular Health Assessment</h2>

          {!result ? (
            <>
              <p>Enter medical parameters or upload a cardiac report (PDF)</p>

              <div className="upload-section">
                <p style={{ marginBottom: "10px", color: "#555" }}>📁 Upload Cardiac Report (Optional)</p>
                <input type="file" accept=".pdf" onChange={handleFileChange} />
              </div>

              <div className="form-grid">
                {Object.keys(formData).map((field) => {
                  const info = HEART_METRICS_INFO[field];
                  if (!info) return null;

                  return (
                    <div className="form-group" key={field}>
                      <label>
                        {info.label}
                        <button
                          className="info-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            setActiveTooltip(activeTooltip === field ? null : field);
                          }}
                        >
                          <HelpCircle size={14} />
                        </button>

                        {activeTooltip === field && (
                          <div className="tooltip-popover" onClick={(e) => e.stopPropagation()}>
                            <strong>{info.label}</strong>
                            <p>{info.info}</p>
                            <div className="range-box">{info.range}</div>
                          </div>
                        )}
                      </label>

                      {info.type === "select" ? (
                        <select
                          name={field}
                          value={formData[field]}
                          onChange={handleChange}
                          className="heart-input"
                        >
                          <option value="">Select {info.label}</option>
                          {info.options.map(opt => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                          ))}
                        </select>
                      ) : (
                        <input
                          type="number"
                          name={field}
                          value={formData[field]}
                          onChange={handleChange}
                          placeholder={info.placeholder}
                          className="heart-input"
                        />
                      )}
                    </div>
                  );
                })}
              </div>

              <button className="predict-btn" onClick={handleSubmit}>
                Analyze Heart Health
              </button>
            </>
          ) : (
            <div className="result-dashboard">
              <div className="result-header" style={{ textAlign: "center", marginBottom: "20px" }}>
                <h3 style={{
                  color: result.prediction === "Heart Disease Detected" ? "#d32f2f" : "#2e7d32",
                  fontSize: "24px", margin: "0"
                }}>
                  {result.prediction}
                </h3>
                <div style={{
                  display: "inline-block", padding: "5px 15px", borderRadius: "15px",
                  background: result.risk_level === "High" ? "#ffcdd2" : result.risk_level === "Moderate" ? "#fff9c4" : "#c8e6c9",
                  color: result.risk_level === "High" ? "#c62828" : result.risk_level === "Moderate" ? "#fbc02d" : "#2e7d32",
                  fontWeight: "bold", fontSize: "14px", marginTop: "10px"
                }}>
                  Risk Level: {result.risk_level} ({result.probability}%)
                </div>
                <p style={{ marginTop: "15px", color: "#555", fontStyle: "italic", background: "#f0f4f8", padding: "10px", borderRadius: "8px" }}>
                  " {result.clinical_summary} "
                </p>
              </div>

              {result.input_details && Object.values(result.input_details).some(d => d.source === "Estimated") && (
                <div style={{ marginTop: "15px", padding: "10px", background: "#fff3cd", color: "#856404", borderRadius: "5px", fontSize: "14px", border: "1px solid #ffeeba" }}>
                  <strong>Note:</strong> Some health values were estimated using dataset medians because they were missing from your input/report.
                </div>
              )}

              <HealthCharts data={result.input_data} diseaseType="heart" />

              <div className="action-buttons" style={{ marginTop: "30px", display: "flex", gap: "15px", flexWrap: "wrap" }}>
                <button
                  onClick={() => navigate(`/hospitals?department=${result.recommended_department}`)}
                  style={{ flex: 1, background: "#00c853", color: "white", padding: "12px", borderRadius: "8px", border: "none", cursor: "pointer", fontWeight: "600" }}
                >
                  Book {result.recommended_department} Specialist
                </button>

                <button
                  onClick={async () => {
                    try {
                      const response = await fetch("http://127.0.0.1:5001/generate_report", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                          patient_data: result.input_details,
                          prediction: result.prediction,
                          risk_level: result.risk_level,
                          clinical_summary: result.clinical_summary,
                          disease_type: "heart",
                          email: localStorage.getItem("email"),
                          patient_name: result.patient_name,
                          gender: result.patient_sex || gender
                        })
                      });
                      if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `Health_Report_${new Date().getTime()}.pdf`;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                      }
                    } catch (e) {
                      console.error("Download failed", e);
                    }
                  }}
                  style={{ flex: 1, background: "#2196f3", color: "white", padding: "12px", borderRadius: "8px", border: "none", cursor: "pointer", fontWeight: "600" }}
                >
                  Download Report
                </button>

                <button
                  onClick={() => setResult(null)}
                  style={{ flex: 1, background: "#eee", color: "#333", padding: "12px", borderRadius: "8px", border: "none", cursor: "pointer", fontWeight: "600" }}
                >
                  Check Another Patient
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Heart;
