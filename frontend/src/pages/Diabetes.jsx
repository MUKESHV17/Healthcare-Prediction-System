import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import HealthCharts from "../components/HealthCharts";
import "./Diabetes.css";

function Diabetes() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    Pregnancies: "",
    Glucose: "",
    BloodPressure: "",
    SkinThickness: "",
    Insulin: "",
    BMI: "",
    DiabetesPedigreeFunction: "",
    Age: ""
  });
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [gender, setGender] = useState("Female"); // Default or fetched

  useEffect(() => {
    const email = localStorage.getItem("email");
    if (email) {
      fetch(`http://127.0.0.1:5001/api/user/profile?email=${email}`)
        .then((res) => res.json())
        .then((data) => {
          if (!data.error) {
            let bmi = "";
            const weight = parseFloat(data.weight);
            const height = parseFloat(data.height);

            if (!isNaN(weight) && !isNaN(height) && height > 0) {
              const hM = height / 100;
              bmi = (weight / (hM * hM)).toFixed(2);
            }
            setFormData((prev) => ({
              ...prev,
              Age: data.age || prev.Age,
              BMI: bmi || prev.BMI,
              Pregnancies: (String(data.gender).toLowerCase() === "male") ? "0" : prev.Pregnancies,
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
      const response = await fetch("http://127.0.0.1:5001/predict/diabetes", {
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
            disease_type: "diabetes",
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
    <div className="diabetes-container">
      <Sidebar />

      <div className="diabetes-main">
        <div className="diabetes-card" style={{ maxWidth: result ? "900px" : "500px", transition: "all 0.3s" }}>
          <h2>Diabetes Prediction</h2>

          {!result ? (
            <>
              <p>Enter patient medical details or upload a lab report (PDF)</p>

              <div style={{ marginBottom: "20px", padding: "15px", border: "1px dashed #ccc", borderRadius: "10px", background: "#f9f9f9", textAlign: "center" }}>
                <p style={{ marginBottom: "10px", color: "#555" }}>📁 Upload Lab Report (Optional)</p>
                <input type="file" accept=".pdf" onChange={handleFileChange} />
              </div>

              <div className="form-grid">
                {Object.keys(formData).map((field) => {
                  const isPregnancies = field === "Pregnancies";
                  const isLocked = isPregnancies && String(gender).toLowerCase() === "male";

                  let label = field.replace(/([A-Z])/g, ' $1').trim();
                  let placeholder = `Enter ${label}`;
                  let hint = "";

                  if (field === "DiabetesPedigreeFunction") {
                    label = "Family History Factor";
                    placeholder = "e.g., 0.37 (Check lab report)";
                    hint = "Score representing genetic risk based on family history.";
                  }

                  return (
                    <div className="form-group" key={field} style={{ opacity: isLocked ? 0.6 : 1 }}>
                      <label>
                        {label}
                        {isLocked && <span style={{ fontSize: "11px", color: "#d32f2f", marginLeft: "5px" }}>(Locked for Male)</span>}
                      </label>
                      <input
                        type="number"
                        name={field}
                        value={formData[field]}
                        onChange={handleChange}
                        placeholder={placeholder}
                        disabled={isLocked}
                        title={hint}
                      />
                      {hint && <p style={{ fontSize: "11px", color: "#666", margin: "4px 0 0" }}>{hint}</p>}
                    </div>
                  );
                })}
              </div>

              <button className="predict-btn" onClick={handleSubmit}>
                Predict Health Status
              </button>
            </>
          ) : (
            <div className="result-dashboard">
              <div className="result-header" style={{ textAlign: "center", marginBottom: "20px" }}>
                <h3 style={{
                  color: result.prediction === "Diabetic" ? "#d32f2f" : "#2e7d32",
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

              <HealthCharts data={result.input_data} diseaseType="diabetes" />

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
                          disease_type: "diabetes",
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

export default Diabetes;
