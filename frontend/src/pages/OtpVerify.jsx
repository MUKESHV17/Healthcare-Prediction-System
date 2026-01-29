import { useState, useRef } from "react";
import "./Otp.css";
import { useNavigate } from "react-router-dom";

function OtpVerify() {
  const [otp, setOtp] = useState("");
  const otpRefs = useRef([]);
  const navigate = useNavigate();

  const handleOtpChange = (e, index) => {
    const value = e.target.value.replace(/\D/, "");
    if (!value) return;

    const otpArr = otp.split("");
    otpArr[index] = value;
    setOtp(otpArr.join(""));

    if (index < 5) {
      otpRefs.current[index + 1].focus();
    }
  };

  const handleOtpBackspace = (e, index) => {
    if (e.key !== "Backspace") return;

    const otpArr = otp.split("");

    if (otpArr[index]) {
      otpArr[index] = "";
      setOtp(otpArr.join(""));
      return;
    }

    if (index > 0) {
      otpRefs.current[index - 1].focus();
      otpArr[index - 1] = "";
      setOtp(otpArr.join(""));
    }
  };

  const handleVerify = async () => {
  if (otp.length !== 6) {
    alert("Enter complete OTP");
    return;
  }

  const phone = localStorage.getItem("phone");

  const res = await fetch("http://127.0.0.1:5000/verify-otp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone, otp })
  });

  const data = await res.json();

  if (res.ok) {
    localStorage.setItem("token", data.token);
    navigate("/dashboard");
  } else {
    alert(data.error);
  }
};

  return (
    <div className="otp-page">
      <div className="otp-card">
        <h2>Verify OTP</h2>
        <p>Enter the 6-digit OTP sent to your mobile</p>

        <div className="otp-boxes">
          {[...Array(6)].map((_, index) => (
            <input
              key={index}
              maxLength="1"
              ref={(el) => (otpRefs.current[index] = el)}
              onChange={(e) => handleOtpChange(e, index)}
              onKeyDown={(e) => handleOtpBackspace(e, index)}
            />
          ))}
        </div>

        <button onClick={handleVerify} className="verify-btn">
          Verify OTP
        </button>
      </div>
    </div>
  );
}

export default OtpVerify;
