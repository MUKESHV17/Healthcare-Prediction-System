import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { Check, X, Calendar, Clock, User } from "lucide-react";

function DoctorDashboard() {
    const [appointments, setAppointments] = useState([]);
    const email = localStorage.getItem("email");

    useEffect(() => {
        if (email) {
            fetchAppointments();
        }
    }, [email]);

    const fetchAppointments = async () => {
        const res = await fetch(`http://127.0.0.1:5000/appointments?email=${email}&role=doctor`);
        const data = await res.json();
        setAppointments(data);
    };

    const handleStatusUpdate = async (id, status) => {
        const res = await fetch("http://127.0.0.1:5000/appointment/status", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id, status })
        });
        if (res.ok) {
            fetchAppointments();
        }
    };

    return (
        <div style={{ display: "flex", height: "100vh", background: "#f8fafc" }}>
            <Sidebar />
            <div style={{ flex: 1, padding: "40px", overflowY: "auto" }}>
                <h2 style={{ marginBottom: "30px" }}>Doctor Dashboard</h2>

                <div style={{ background: "white", padding: "30px", borderRadius: "20px", boxShadow: "0 4px 15px rgba(0,0,0,0.05)" }}>
                    <h3 style={{ marginBottom: "20px" }}>Appointment Requests</h3>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                            <tr style={{ textAlign: "left", borderBottom: "2px solid #eee" }}>
                                <th style={{ padding: "12px" }}>Patient Name</th>
                                <th style={{ padding: "12px" }}>Date</th>
                                <th style={{ padding: "12px" }}>Time</th>
                                <th style={{ padding: "12px" }}>Status</th>
                                <th style={{ padding: "12px" }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {appointments.map(app => (
                                <tr key={app.id} style={{ borderBottom: "1px solid #eee" }}>
                                    <td style={{ padding: "12px", display: "flex", alignItems: "center", gap: "10px" }}>
                                        <div style={{ width: "32px", height: "32px", background: "#e8f5e9", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}>
                                            <User size={16} color="#2e7d32" />
                                        </div>
                                        {app.name}
                                    </td>
                                    <td style={{ padding: "12px" }}>{app.date}</td>
                                    <td style={{ padding: "12px" }}>{app.time}</td>
                                    <td style={{ padding: "12px" }}>
                                        <span style={{
                                            padding: "4px 10px",
                                            borderRadius: "20px",
                                            fontSize: "12px",
                                            fontWeight: "600",
                                            background: app.status === "Confirmed" ? "#e8f5e9" : app.status === "Rejected" ? "#ffebee" : "#fff3e0",
                                            color: app.status === "Confirmed" ? "#2e7d32" : app.status === "Rejected" ? "#c62828" : "#ef6c00"
                                        }}>
                                            {app.status}
                                        </span>
                                    </td>
                                    <td style={{ padding: "12px" }}>
                                        {app.status === "Pending Confirmation" && (
                                            <div style={{ display: "flex", gap: "10px" }}>
                                                <button
                                                    onClick={() => handleStatusUpdate(app.id, "Confirmed")}
                                                    style={{ background: "#00c853", color: "white", border: "none", padding: "6px 12px", borderRadius: "6px", cursor: "pointer", display: "flex", alignItems: "center", gap: "5px" }}
                                                >
                                                    <Check size={14} /> Accept
                                                </button>
                                                <button
                                                    onClick={() => handleStatusUpdate(app.id, "Rejected")}
                                                    style={{ background: "#ff5252", color: "white", border: "none", padding: "6px 12px", borderRadius: "6px", cursor: "pointer", display: "flex", alignItems: "center", gap: "5px" }}
                                                >
                                                    <X size={14} /> Reject
                                                </button>
                                            </div>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {appointments.length === 0 && <p style={{ textAlign: "center", padding: "40px", color: "#888" }}>No appointments found.</p>}
                </div>
            </div>
        </div>
    );
}

export default DoctorDashboard;
