import { Routes, Route, Navigate } from "react-router-dom";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Diabetes from "./pages/Diabetes";
import Heart from "./pages/Heart";
import OtpVerify from "./pages/OtpVerify";
import Profile from "./pages/Profile";




const isAuthenticated = () => {
  return localStorage.getItem("isLoggedIn") === "true";
};

function App() {
  return (
    <Routes>
      <Route path="/signup" element={<Signup />} />
      <Route path="/login" element={<Login />} />


      <Route path="/verify-otp" element={<OtpVerify />} />
      <Route
        path="/diabetes"
        element={isAuthenticated() ? <Diabetes /> : <Navigate to="/login" />}
      />

      <Route
        path="/heart"
        element={isAuthenticated() ? <Heart /> : <Navigate to="/login" />}
      />


      <Route path="/heart" element={<div>Heart Disease Page</div>} />
      <Route
        path="/diabetes"
        element={isAuthenticated() ? <Diabetes /> : <Navigate to="/login" />}
      />


      <Route
        path="/dashboard"
        element={
          isAuthenticated() ? <Dashboard /> : <Navigate to="/login" />
        }
      />

      <Route
        path="/profile"
        element={
          isAuthenticated() ? <Profile /> : <Navigate to="/login" />
        }
      />

      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}

export default App;
