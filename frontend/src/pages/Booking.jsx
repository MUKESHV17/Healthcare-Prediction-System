import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { useLocation, useNavigate } from "react-router-dom";
import { Calendar as CalendarIcon, Clock, User, CheckCircle } from "lucide-react";

function Booking() {
    const location = useLocation();
    const navigate = useNavigate();
    const queryParams = new URLSearchParams(location.search);
    const hospitalId = queryParams.get("hospital_id");
    const dept = queryParams.get("department");

    const [doctors, setDoctors] = useState([]);
    const [selectedDoctor, setSelectedDoctor] = useState(null);
    const [selectedDate, setSelectedDate] = useState("");
    const [selectedSlot, setSelectedSlot] = useState("");
    const [message, setMessage] = useState("");

    useEffect(() => {
        if (hospitalId) {
            fetch(`http://127.0.0.1:5001/doctors?hospital_id=${hospitalId}&department=${dept}`)
                .then(res => res.json())
                .then(data => setDoctors(data));
        }
    }, [hospitalId, dept]);

    const handleBook = async () => {
        if (!selectedDoctor || !selectedDate || !selectedSlot) {
            alert("Please select doctor, date and slot");
            return;
        }

        const res = await fetch("http://127.0.0.1:5001/bookings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                patientEmail: localStorage.getItem("email"),
                doctorId: selectedDoctor.id,
                hospitalId: hospitalId,
                date: selectedDate,
                timeSlot: selectedSlot
            })
        });

        const data = await res.json();
        if (res.ok) {
            setMessage("Booking successful! Redirecting to Dashboard...");
            setTimeout(() => navigate("/dashboard"), 3000);
        } else {
            alert(data.error);
        }
    };

    return (
        <div style={{ display: "flex", height: "100vh", background: "#f8fafc" }}>
            <Sidebar />
            <div style={{ flex: 1, padding: "40px", overflowY: "auto" }}>
                {/* Confirmation View */}
                {message && message.includes("successful") ? (
                    <div style={{ textAlign: "center", padding: "40px", background: "white", borderRadius: "20px", boxShadow: "0 10px 25px rgba(0,0,0,0.1)", maxWidth: "500px", margin: "0 auto" }}>
                        <div style={{ width: "80px", height: "80px", background: "#e8f5e9", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px" }}>
                            <CheckCircle size={40} color="#2e7d32" />
                        </div>
                        <h2 style={{ color: "#2e7d32", marginBottom: "10px" }}>Appointment Confirmed!</h2>
                        <p style={{ color: "#666", marginBottom: "30px" }}>Your appointment has been successfully scheduled.</p>

                        <div style={{ background: "#f8fafc", padding: "20px", borderRadius: "15px", textAlign: "left", marginBottom: "30px" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                                <span style={{ color: "#888", fontSize: "14px" }}>Hospital</span>
                                <span style={{ fontWeight: "600" }}>{doctors[0]?.hospitalId} (ID)</span> {/* In real app, fetch hospital name or pass it */}
                            </div>
                            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                                <span style={{ color: "#888", fontSize: "14px" }}>Department</span>
                                <span style={{ fontWeight: "600" }}>{dept}</span>
                            </div>
                            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                                <span style={{ color: "#888", fontSize: "14px" }}>Doctor</span>
                                <span style={{ fontWeight: "600" }}>{selectedDoctor?.name}</span>
                            </div>
                            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                                <span style={{ color: "#888", fontSize: "14px" }}>Date</span>
                                <span style={{ fontWeight: "600" }}>{selectedDate}</span>
                            </div>
                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "#888", fontSize: "14px" }}>Time</span>
                                <span style={{ fontWeight: "600" }}>{selectedSlot}</span>
                            </div>
                        </div>

                        <button
                            onClick={() => navigate("/dashboard")}
                            style={{ background: "#00c853", color: "white", border: "none", padding: "12px 30px", borderRadius: "10px", fontSize: "16px", cursor: "pointer", fontWeight: "600", width: "100%" }}
                        >
                            Go to Dashboard
                        </button>
                    </div>
                ) : (
                    <>
                        <h2 style={{ marginBottom: "20px" }}>Book Appointment</h2>
                        {message && (
                            <div style={{ background: "#ffebee", color: "#c62828", padding: "15px", borderRadius: "10px", marginBottom: "20px" }}>
                                {message}
                            </div>
                        )}
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "30px" }}>
                            {/* Doctors List */}
                            <div style={{ background: "white", padding: "20px", borderRadius: "20px", boxShadow: "0 4px 15px rgba(0,0,0,0.05)" }}>
                                <h3 style={{ marginBottom: "20px" }}>Select Doctor ({dept})</h3>
                                <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
                                    {doctors.map(doc => (
                                        <div
                                            key={doc.id}
                                            onClick={() => setSelectedDoctor(doc)}
                                            style={{
                                                padding: "15px",
                                                borderRadius: "12px",
                                                border: `2px solid ${selectedDoctor?.id === doc.id ? "#00c853" : "#eee"}`,
                                                cursor: "pointer",
                                                background: selectedDoctor?.id === doc.id ? "#f1fbf4" : "white"
                                            }}
                                        >
                                            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                                                <div style={{ width: "40px", height: "40px", background: "#eee", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}>
                                                    <User size={20} color="#666" />
                                                </div>
                                                <div>
                                                    <h4 style={{ margin: 0 }}>{doc.name}</h4>
                                                    <p style={{ margin: 0, fontSize: "12px", color: "#666" }}>{doc.specialty} • {doc.experience} yrs exp</p>
                                                    <p style={{ margin: "2px 0 0 0", fontSize: "11px", color: "#00c853", background: "#f0fdf4", padding: "2px 5px", borderRadius: "4px", display: "inline-block" }}>
                                                        📧 Login: {doc.email}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Date & Slot Selection */}
                            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                                <div style={{ background: "white", padding: "20px", borderRadius: "20px", boxShadow: "0 4px 15px rgba(0,0,0,0.05)" }}>
                                    <h3 style={{ marginBottom: "20px", display: "flex", alignItems: "center", gap: "10px" }}>
                                        <CalendarIcon size={20} color="#00c853" /> Select Date
                                    </h3>
                                    <input
                                        type="date"
                                        value={selectedDate}
                                        onChange={(e) => setSelectedDate(e.target.value)}
                                        style={{ width: "100%", padding: "12px", borderRadius: "10px", border: "1px solid #ddd" }}
                                    />
                                </div>

                                {selectedDoctor && (
                                    <div style={{ background: "white", padding: "20px", borderRadius: "20px", boxShadow: "0 4px 15px rgba(0,0,0,0.05)" }}>
                                        <h3 style={{ marginBottom: "20px", display: "flex", alignItems: "center", gap: "10px" }}>
                                            <Clock size={20} color="#00c853" /> Available Slots
                                        </h3>
                                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                                            {selectedDoctor.availability.map(slot => (
                                                <button
                                                    key={slot}
                                                    onClick={() => setSelectedSlot(slot)}
                                                    style={{
                                                        padding: "10px",
                                                        borderRadius: "8px",
                                                        border: "1px solid #ddd",
                                                        background: selectedSlot === slot ? "#00c853" : "white",
                                                        color: selectedSlot === slot ? "white" : "#333",
                                                        cursor: "pointer",
                                                        fontWeight: "600"
                                                    }}
                                                >
                                                    {slot}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <button
                                    disabled={!selectedDoctor || !selectedDate || !selectedSlot}
                                    onClick={handleBook}
                                    style={{
                                        padding: "15px",
                                        borderRadius: "12px",
                                        background: "#00c853",
                                        color: "white",
                                        border: "none",
                                        fontSize: "16px",
                                        fontWeight: "700",
                                        cursor: "pointer",
                                        opacity: (!selectedDoctor || !selectedDate || !selectedSlot) ? 0.6 : 1
                                    }}
                                >
                                    Confirm Appointment
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default Booking;
