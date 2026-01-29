import Sidebar from "../components/Sidebar";
import { useState } from "react";
import "./Diabetes.css"; // reuse same professional styles

function Heart() {
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

  const [result, setResult] = useState("");


  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };
  const handleSubmit = async () => {
    const response = await fetch("http://127.0.0.1:5000/predict/heart", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        age: Number(formData.age),
        sex: Number(formData.sex),
        cp: Number(formData.cp),
        trestbps: Number(formData.trestbps),
        chol: Number(formData.chol),
        fbs: Number(formData.fbs),
        restecg: Number(formData.restecg),
        thalach: Number(formData.thalach),
        exang: Number(formData.exang),
        oldpeak: Number(formData.oldpeak),
        slope: Number(formData.slope),
        ca: Number(formData.ca),
        thal: Number(formData.thal)
      })
    });

    const data = await response.json();
    setResult(data.prediction || data.error);
  };


  return (
    <div className="diabetes-container">
      <Sidebar />

      <div className="diabetes-main">
        <div className="diabetes-card">
          <h2>Heart Disease Prediction</h2>
          <p>Enter patient cardiovascular details</p>

          <div className="form-grid">
            {Object.keys(formData).map((field) => (
              <div className="form-group" key={field}>
                <label>{field.toUpperCase()}</label>
                <input
                  type="number"
                  name={field}
                  value={formData[field]}
                  onChange={handleChange}
                  placeholder={`Enter ${field}`}
                />
              </div>
            ))}
          </div>

          <button className="predict-btn" onClick={handleSubmit}>
            Predict Heart Disease
          </button>
          {result && (
            <div className="result-box">
              Result: {result}
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default Heart;
