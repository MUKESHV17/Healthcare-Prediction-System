import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { MessageCircle } from "lucide-react";
import ChatWindow from "./ChatWindow";

function Appointments() {
    const [appointments, setAppointments] = useState([]);
    const userId = parseInt(localStorage.getItem("userId"));

    // Chat State
    const [chatOpen, setChatOpen] = useState(false);
    const [activeRoom, setActiveRoom] = useState(null);
    const [chatReceiverId, setChatReceiverId] = useState(null);
    const [contactName, setContactName] = useState("");

    useEffect(() => {
        const email = localStorage.getItem("email");
        if (email) {
            fetch(`http://127.0.0.1:5001/appointments?email=${email}`)
                .then(res => res.json())
                .then(data => {
                    if (Array.isArray(data)) setAppointments(data);
                })
                .catch(err => console.error(err));
        }
    }, []);

    const openChat = (app) => {
        if (!app.doctorId) {
            alert("Error: Doctor ID not found");
            return;
        }

        const pId = userId;
        const dId = app.doctorId;

        // Same logic: chat_{min}_{max} to match Doctor's room
        const room = `chat_${Math.min(pId, dId)}_${Math.max(pId, dId)}`;

        setActiveRoom(room);
        setChatReceiverId(dId);
        setContactName(app.name);
        setChatOpen(true);
    };

    return (
        <div style={{ display: "flex", height: "100vh", background: "#f8fafc" }}>
            <Sidebar />
            <div style={{ flex: 1, padding: "40px", overflowY: "auto" }}>
                <h2>My Appointments</h2>
                <div style={{ marginTop: "20px", background: "white", padding: "20px", borderRadius: "10px", boxShadow: "0 2px 10px rgba(0,0,0,0.05)" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                            <tr style={{ borderBottom: "1px solid #eee", textAlign: "left" }}>
                                <th style={{ padding: "10px" }}>Hospital</th>
                                <th style={{ padding: "10px" }}>Doctor</th>
                                <th style={{ padding: "10px" }}>Date</th>
                                <th style={{ padding: "10px" }}>Time</th>
                                <th style={{ padding: "10px" }}>Status</th>
                                <th style={{ padding: "10px" }}>Chat</th>
                            </tr>
                        </thead>
                        <tbody>
                            {appointments.length > 0 ? appointments.map((app) => (
                                <tr key={app.id} style={{ borderBottom: "1px solid #f9f9f9" }}>
                                    <td style={{ padding: "10px" }}>{app.hospital}</td>
                                    <td style={{ padding: "10px" }}>{app.name}</td>
                                    <td style={{ padding: "10px" }}>{app.date}</td>
                                    <td style={{ padding: "10px" }}>{app.time}</td>
                                    <td style={{ padding: "10px" }}>
                                        <span style={{
                                            padding: "4px 10px", borderRadius: "20px", fontSize: "12px", fontWeight: "600",
                                            background: app.status === "Confirmed" ? "#e8f5e9" : app.status === "Rejected" ? "#ffebee" : "#fff3e0",
                                            color: app.status === "Confirmed" ? "#2e7d32" : app.status === "Rejected" ? "#c62828" : "#ef6c00"
                                        }}>
                                            {app.status}
                                        </span>
                                    </td>
                                    <td style={{ padding: "10px" }}>
                                        <button
                                            onClick={() => openChat(app)}
                                            style={{ background: "#2196f3", color: "white", border: "none", padding: "8px", borderRadius: "50%", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}
                                            title="Chat with Doctor"
                                        >
                                            <MessageCircle size={16} />
                                        </button>
                                    </td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan="6" style={{ textAlign: "center", padding: "20px" }}>No appointments found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <ChatWindow
                isOpen={chatOpen}
                onClose={() => setChatOpen(false)}
                roomId={activeRoom}
                currentUserId={userId}
                receiverId={chatReceiverId}
                contactName={contactName}
            />
        </div>
    );
}

export default Appointments;
