import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import "./Dashboard.css";
import { Search, Mail, Bell, Activity, Heart } from "lucide-react";

function Dashboard() {
  const [user, setUser] = useState({
    firstName: localStorage.getItem("firstName") || "User",
    profilePic: ""
  });
  const navigate = useNavigate();

  useEffect(() => {
    const email = localStorage.getItem("email");
    if (email) {
      fetch(`http://127.0.0.1:5000/profile?email=${email}`)
        .then(res => res.json())
        .then(data => {
          if (data.firstName) {
            setUser(data);
          }
        })
        .catch(err => console.error("Failed to load profile", err));
    }
  }, []);

  return (
    <div className="dashboard-container">
      <Sidebar />

      <div className="dashboard-content">
        {/* Header */}
        <div className="dashboard-header">
          <h2 style={{ margin: 0 }}>Dashboard</h2>

          <div className="search-bar">
            <Search size={18} color="#999" />
            <input type="text" placeholder="Search" />
          </div>

          <div className="header-actions">
            <button className="icon-btn"><Mail size={20} /></button>
            <button className="icon-btn"><Bell size={20} /></button>
            <img
              src={user.profilePic || "https://randomuser.me/api/portraits/men/32.jpg"}
              alt="Profile"
              className="user-profile-img"
              onClick={() => navigate("/profile")}
              style={{ cursor: "pointer" }}
            />
          </div>
        </div>

        {/* Welcome Banner */}
        <div className="welcome-banner">
          <div className="welcome-text">
            <h1>Hi, {user.firstName}</h1>
            <h1>Check your Health!</h1>
            <p>Here’s your health at a glance. You're doing great this week!</p>
            <button className="schedule-btn">Schedule Appointment</button>
          </div>
          {/* Using a placeholder SVG or image for the doctor illustration */}
          <div className="doctor-illustration">
            {/* You would typically place a transparent PNG here */}
            <img src="https://png.pngtree.com/png-clipart/20250609/original/pngtree-cute-cartoon-doctor-boy-illustration-pediatric-medical-character-png-image_21148068.png" alt="Doctor" style={{ height: "100%" }} />
          </div>
        </div>

        {/* Middle Stats Grid */}
        <div className="stats-grid" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>

          {/* Heartbeat Card */}
          <div className="stat-card">
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="stat-label">Heartbeat</span>
              <Activity size={20} color="#666" />
            </div>

            {/* Simple SVG Graph Mockup */}
            <svg className="heart-graph" viewBox="0 0 100 25">
              <polyline points="0,15 10,15 15,5 20,20 25,10 30,15 100,15" stroke="#2196f3" fill="none" />
            </svg>

            <div style={{ display: "flex", alignItems: "baseline", gap: "10px" }}>
              <span className="stat-value">86</span>
              <span className="stat-label" style={{ fontSize: "16px" }}>bpm</span>
              <span style={{ fontSize: "12px", color: "green", background: "#e8f5e9", padding: "2px 8px", borderRadius: "10px" }}>norm</span>
            </div>
          </div>

          {/* Avg Diagnose Mockup */}
          <div className="stat-card">
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="stat-label">Avg Diagnose</span>
            </div>
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%" }}>
              {/* CSS Donut Chart Mockup */}
              <div style={{
                width: "80px", height: "80px", borderRadius: "50%",
                background: "conic-gradient(#00c853 0% 75%, #eeeeee 75% 100%)",
                display: "flex", alignItems: "center", justifyContent: "center"
              }}>
                <div style={{ width: "60px", height: "60px", background: "white", borderRadius: "50%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                  <span style={{ fontSize: "10px", color: "#888" }}>Total</span>
                  <span style={{ fontWeight: "bold" }}>750</span>
                </div>
              </div>
            </div>
          </div>

          {/* Weekly Summary */}
          <div className="stat-card">
            <span className="stat-label">Weekly Health</span>
            <div style={{ display: "flex", justifyContent: "space-around", marginTop: "20px" }}>
              <div style={{ textAlign: "center" }}>
                <span style={{ display: "block", fontSize: "12px", color: "#888" }}>Vitals</span>
                <span style={{ fontSize: "24px", color: "#00c853", fontWeight: "bold" }}>A</span>
              </div>
              <div style={{ textAlign: "center" }}>
                <span style={{ display: "block", fontSize: "12px", color: "#888" }}>Meds</span>
                <span style={{ fontSize: "24px", color: "#2196f3", fontWeight: "bold" }}>B+</span>
              </div>
            </div>
          </div>

        </div>

        {/* Bottom Section */}
        <div className="bottom-grid">

          {/* Appointments */}
          <div className="appointments-section">
            <div className="section-header">Appointment</div>
            <table className="appointments-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Dr Name</th>
                  <th>Phone</th>
                  <th>Date</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>#ID12377</td>
                  <td>
                    <div className="doctor-info-cell">
                      <span>Abdul Khodr</span>
                    </div>
                  </td>
                  <td>(+91) 2237363</td>
                  <td>July 6, 2025</td>
                  <td>10:30 AM</td>
                </tr>
                <tr>
                  <td>#ID12378</td>
                  <td>
                    <div className="doctor-info-cell">
                      <span>Franklin Kondang</span>
                    </div>
                  </td>
                  <td>(+91) 2237363</td>
                  <td>July 7, 2025</td>
                  <td>10:30 AM</td>
                </tr>
                <tr>
                  <td>#ID12377</td>
                  <td>
                    <div className="doctor-info-cell">
                      <span>Abdul Khodr</span>
                    </div>
                  </td>
                  <td>(+91) 2237363</td>
                  <td>July 8, 2025</td>
                  <td>10:30 AM</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Latest Visits */}
          <div className="visits-section">
            <div className="section-header">Latest Visits</div>

            {[
              { name: "Esther Howard", spec: "Dermatology", time: "10:30 AM", img: "https://randomuser.me/api/portraits/women/44.jpg" },
              { name: "Eleanor Pena", spec: "Gastroenterology", time: "12:30 AM", img: "https://randomuser.me/api/portraits/women/68.jpg" },
              { name: "Brooklyn Simmons", spec: "Ophthalmology", time: "2:00 AM", img: "https://randomuser.me/api/portraits/men/85.jpg" },
              { name: "Cameron Williamson", spec: "Rheumatology", time: "3:30 AM", img: "https://randomuser.me/api/portraits/men/33.jpg" }
            ].map((doctor, idx) => (
              <div className="visit-item" key={idx}>
                <div className="visit-info">
                  <img src={doctor.img} alt={doctor.name} className="visit-img" />
                  <div className="visit-details">
                    <h5>{doctor.name}</h5>
                    <p>{doctor.spec}</p>
                  </div>
                </div>
                <span className="visit-time">{doctor.time}</span>
              </div>
            ))}

          </div>

        </div>

      </div>
    </div>
  );
}

export default Dashboard;
