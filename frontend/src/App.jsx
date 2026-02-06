import { Routes, Route, Navigate } from "react-router-dom";
import React, { useEffect, useState, Suspense, lazy } from "react";
import { CheckCircle, XCircle, Info } from "lucide-react";
import { io } from "socket.io-client";

// Lazy Loaded Pages
const Signup = lazy(() => import("./pages/Signup"));
const Login = lazy(() => import("./pages/Login"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Diabetes = lazy(() => import("./pages/Diabetes"));
const Heart = lazy(() => import("./pages/Heart"));
const OtpVerify = lazy(() => import("./pages/OtpVerify"));
const Profile = lazy(() => import("./pages/Profile"));
const Hospitals = lazy(() => import("./pages/Hospitals"));
const Booking = lazy(() => import("./pages/Booking"));
const Appointments = lazy(() => import("./pages/Appointments"));
const DoctorDashboard = lazy(() => import("./pages/DoctorDashboard"));
const History = lazy(() => import("./pages/History"));

const socket = io("http://127.0.0.1:5000");

const isAuthenticated = () => {
  return localStorage.getItem("isLoggedIn") === "true";
};

// Error Boundary for UI stability
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(error, errorInfo) { console.error("MedPro Crash:", error, errorInfo); }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "100px 20px", textAlign: "center", background: "#f8f9fa", minHeight: "100vh" }}>
          <h2>Oops! Something went wrong.</h2>
          <p>The application encountered an unexpected error.</p>
          <button onClick={() => window.location.reload()} style={{ padding: "10px 20px", background: "#3498db", color: "#fff", border: "none", borderRadius: "8px", cursor: "pointer" }}>Reload App</button>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    socket.on("notification", (data) => {
      if (data.email === localStorage.getItem("email")) {
        const type = data.message.toLowerCase().includes("approved") ? "success" :
          data.message.toLowerCase().includes("rejected") ? "error" : "info";
        setNotification({ msg: data.message, type });
        setTimeout(() => setNotification(null), 6000);
      }
    });
    return () => socket.off("notification");
  }, []);

  return (
    <ErrorBoundary>
      {notification && (
        <div style={{
          position: "fixed", top: "30px", right: "30px",
          background: notification.type === "success" ? "#e8f5e9" : notification.type === "error" ? "#ffebee" : "#e3f2fd",
          color: notification.type === "success" ? "#2e7d32" : notification.type === "error" ? "#c62828" : "#1565c0",
          border: `1px solid ${notification.type === "success" ? "#a5d6a7" : notification.type === "error" ? "#ef9a9a" : "#90caf9"}`,
          padding: "16px 24px", borderRadius: "16px", zIndex: 10000,
          boxShadow: "0 15px 35px rgba(0,0,0,0.12)", display: "flex", alignItems: "center", gap: "14px",
          minWidth: "320px", maxWidth: "450px"
        }}>
          {notification.type === "success" ? <CheckCircle size={22} /> : notification.type === "error" ? <XCircle size={22} /> : <Info size={22} />}
          <span style={{ fontWeight: "600" }}>{notification.msg}</span>
        </div>
      )}
      <Suspense fallback={<div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>Loading MedPro...</div>}>
        <Routes>
          <Route path="/signup" element={<Signup />} />
          <Route path="/login" element={<Login />} />
          <Route path="/verify-otp" element={<OtpVerify />} />
          <Route path="/diabetes" element={isAuthenticated() ? <Diabetes /> : <Navigate to="/login" />} />
          <Route path="/heart" element={isAuthenticated() ? <Heart /> : <Navigate to="/login" />} />
          <Route path="/dashboard" element={isAuthenticated() ? <Dashboard /> : <Navigate to="/login" />} />
          <Route path="/profile" element={isAuthenticated() ? <Profile /> : <Navigate to="/login" />} />
          <Route path="/hospitals" element={isAuthenticated() ? <Hospitals /> : <Navigate to="/login" />} />
          <Route path="/booking" element={isAuthenticated() ? <Booking /> : <Navigate to="/login" />} />
          <Route path="/appointments" element={isAuthenticated() ? <Appointments /> : <Navigate to="/login" />} />
          <Route path="/doctor-dashboard" element={isAuthenticated() ? <DoctorDashboard /> : <Navigate to="/login" />} />
          <Route path="/history" element={isAuthenticated() ? <History /> : <Navigate to="/login" />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
}

export default App;
