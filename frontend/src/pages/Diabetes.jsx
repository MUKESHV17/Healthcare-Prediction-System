import Sidebar from "../components/Sidebar";
import { useState } from "react";
import "./Diabetes.css";

function Diabetes() {
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
  const [result, setResult] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async () => {
    const response = await fetch("http://127.0.0.1:5000/predict/diabetes", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        Pregnancies: Number(formData.Pregnancies),
        Glucose: Number(formData.Glucose),
        BloodPressure: Number(formData.BloodPressure),
        SkinThickness: Number(formData.SkinThickness),
        Insulin: Number(formData.Insulin),
        BMI: Number(formData.BMI),
        DiabetesPedigreeFunction: Number(formData.DiabetesPedigreeFunction),
        Age: Number(formData.Age)
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
          <h2>Diabetes Prediction</h2>
          <p>Enter patient medical details</p>

          <div className="form-grid">
            {Object.keys(formData).map((field) => (
              <div className="form-group" key={field}>
                <label>{field.replace(/([A-Z])/g, ' $1').trim()}</label>
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
            Predict Diabetes
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

export default Diabetes;
