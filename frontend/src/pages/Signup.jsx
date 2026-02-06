import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./Signup.css";

function Signup() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    dob: "",
    email: "",
    phone: "",
    city: "",
    pincode: "",
    password: "",
    confirmPassword: "",
    role: "patient"
  });

  const [showPassword, setShowPassword] = useState(false);
  const pincodeRefs = useRef([]);

  // -------------------- COMMON CHANGE HANDLER --------------------
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // -------------------- PINCODE HANDLERS --------------------
  const handlePincodeChange = (e, index) => {
    const value = e.target.value.replace(/\D/, "");
    if (!value) return;

    const pinArray = formData.pincode.split("");
    pinArray[index] = value;

    setFormData({ ...formData, pincode: pinArray.join("") });

    if (index < 5) {
      pincodeRefs.current[index + 1].focus();
    }
  };

  const handlePincodeBackspace = (e, index) => {
    if (e.key !== "Backspace") return;

    const pinArray = formData.pincode.split("");

    if (pinArray[index]) {
      pinArray[index] = "";
      setFormData({ ...formData, pincode: pinArray.join("") });
      return;
    }

    if (index > 0) {
      pincodeRefs.current[index - 1].focus();
      pinArray[index - 1] = "";
      setFormData({ ...formData, pincode: pinArray.join("") });
    }
  };

  // -------------------- SUBMIT --------------------
  const handleSignup = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    const response = await fetch("http://127.0.0.1:5000/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });

    const data = await response.json();

    if (response.ok) {
      // ✅ OTP FLOW HANDOFF
      localStorage.setItem("phone", formData.phone);

      navigate("/verify-otp");
    } else {
      alert(data.error || "Signup failed");
    }
  };

  // -------------------- JSX --------------------
  return (
    <div className="signup-page">
      <div className="signup-card">
        <h2>New Patient Registration</h2>
        <p className="subtitle">Enter your details to create an account</p>

        <form onSubmit={handleSignup} className="signup-form">
          <div className="grid">
            <div className="form-group">
              <label>First Name</label>
              <input
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Role</label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #ddd" }}
              >
                <option value="patient">Patient</option>
                <option value="doctor">Doctor</option>
              </select>
            </div>

            <div className="form-group">
              <label>Last Name</label>
              <input
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Date of Birth</label>
              <div className="date-wrapper">
                <input
                  type="date"
                  name="dob"
                  value={formData.dob}
                  onChange={handleChange}
                />
                <span className="calendar-icon">📅</span>
              </div>
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Phone</label>
              <div className="phone-wrapper">
                <span className="country-code">+91</span>
                <input
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="Enter phone number"
                />
              </div>
            </div>

            <div className="form-group">
              <label>City</label>
              <input
                name="city"
                value={formData.city}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Pincode</label>
              <div className="pincode-boxes">
                {[...Array(6)].map((_, index) => (
                  <input
                    key={index}
                    type="text"
                    maxLength="1"
                    ref={(el) => (pincodeRefs.current[index] = el)}
                    onChange={(e) => handlePincodeChange(e, index)}
                    onKeyDown={(e) => handlePincodeBackspace(e, index)}
                  />
                ))}
              </div>
            </div>
          </div>

          <div className="form-group full">
            <label>Create Password</label>
            <div className="password-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
              />
              <span
                className="eye-icon"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? "🙈" : "👁️"}
              </span>
            </div>
          </div>

          <div className="form-group full">
            <label>Confirm Password</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
            />
          </div>

          <button type="submit" className="signup-btn">
            Create Account
          </button>

          <p className="login-link">
            Already have an account? <a href="/login">Login</a>
          </p>
        </form>
      </div >
    </div >
  );
}

export default Signup;
