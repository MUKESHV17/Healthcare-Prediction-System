import React, { useState, useEffect } from 'react';

const History = () => {
    const [reports, setReports] = useState([]);
    const [error, setError] = useState("");

    const email = localStorage.getItem("email");

    useEffect(() => {
        fetch(`http://127.0.0.1:5001/api/user/reports?email=${email}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) setError(data.error);
                else setReports(data);
            })
            .catch(err => setError("Failed to load history"));
    }, []);

    const downloadPDF = (report) => {
        // Re-download logic or serve stored file
        // For now, simpler to re-trigger generation or serve file if we had a proper file server
        // Since we save 'pdf_path' which is local backend path, we can't fetch it directly via HTTP unless served static
        // Ideally we'd have an endpoint /api/reports/download/:id
        // For MVP phase 4, let's just show alerts or 'View' if we had a viewer
        alert(`Downloading report from: ${report.date}`);
        // In real prod, this would hit /api/user/reports/download/${report.id}
    };

    return (
        <div style={{ maxWidth: "800px", margin: "40px auto", padding: "20px", background: "white", borderRadius: "8px", boxShadow: "0 2px 10px rgba(0,0,0,0.1)" }}>
            <h2 style={{ color: "#2c3e50", borderBottom: "2px solid #eee", paddingBottom: "10px" }}>Medical History</h2>

            {error && <p style={{ color: "red" }}>{error}</p>}

            {reports.length === 0 ? (
                <p>No reports found.</p>
            ) : (
                <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "20px" }}>
                    <thead>
                        <tr style={{ background: "#f8f9fa", textAlign: "left" }}>
                            <th style={{ padding: "12px", borderBottom: "2px solid #ddd" }}>Date</th>
                            <th style={{ padding: "12px", borderBottom: "2px solid #ddd" }}>Type</th>
                            <th style={{ padding: "12px", borderBottom: "2px solid #ddd" }}>Prediction</th>
                            <th style={{ padding: "12px", borderBottom: "2px solid #ddd" }}>Risk</th>
                            <th style={{ padding: "12px", borderBottom: "2px solid #ddd" }}>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reports.map((r) => (
                            <tr key={r.id} style={{ borderBottom: "1px solid #eee" }}>
                                <td style={{ padding: "12px" }}>{r.date}</td>
                                <td style={{ padding: "12px", textTransform: "capitalize" }}>{r.disease_type}</td>
                                <td style={{ padding: "12px", fontWeight: "bold", color: r.prediction.includes("No") ? "green" : "red" }}>
                                    {r.prediction}
                                </td>
                                <td style={{ padding: "12px" }}>
                                    <span style={{
                                        padding: "4px 8px", borderRadius: "12px", fontSize: "12px",
                                        background: r.risk_level === "High" ? "#ffebee" : r.risk_level === "Moderate" ? "#fff3e0" : "#e8f5e9",
                                        color: r.risk_level === "High" ? "#c62828" : r.risk_level === "Moderate" ? "#ef6c00" : "#2e7d32"
                                    }}>
                                        {r.risk_level}
                                    </span>
                                </td>
                                <td style={{ padding: "12px" }}>
                                    <button
                                        onClick={() => downloadPDF(r)}
                                        style={{ padding: "6px 12px", background: "#3498db", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}
                                    >
                                        View Report
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default History;
