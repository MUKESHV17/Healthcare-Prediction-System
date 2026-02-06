import React from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';

const HealthCharts = ({ data, diseaseType }) => {
    if (!data) return null;

    // Prepare Data for Charts
    let barData = [];
    let radarData = [];

    if (diseaseType === "diabetes") {
        barData = [
            { name: 'Glucose', value: data.Glucose, normal: 100, max: 200 },
            { name: 'BP', value: Number(data.BloodPressure), normal: 80, max: 140 },
            { name: 'BMI', value: data.BMI, normal: 25, max: 40 },
            { name: 'Age', value: data.Age, normal: 30, max: 80 },
        ];
        radarData = barData;
    } else if (diseaseType === "heart") {
        barData = [
            { name: 'Cholesterol', value: data.chol, normal: 200, max: 300 },
            { name: 'Resting BP', value: data.trestbps, normal: 120, max: 180 },
            { name: 'Max HR', value: data.thalach, normal: 150, max: 200 },
            { name: 'Age', value: data.age, normal: 50, max: 90 },
        ];
        radarData = barData;
    }

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const val = payload[0].value;
            const item = barData.find(d => d.name === label);
            const isHigh = item && val > item.normal;

            return (
                <div style={{ background: "white", padding: "10px", border: "1px solid #ccc", borderRadius: "5px" }}>
                    <p className="label">{`${label} : ${val}`}</p>
                    <p style={{ color: isHigh ? "red" : "green" }}>
                        {isHigh ? "Above Normal" : "Normal Range"}
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div style={{ marginTop: "20px", display: "flex", flexWrap: "wrap", gap: "20px" }}>

            {/* Bar Chart */}
            <div style={{ flex: "1 1 300px", minWidth: "300px", height: "300px", background: "#fff", padding: "10px", borderRadius: "10px", boxShadow: "0 2px 10px rgba(0,0,0,0.1)" }}>
                <h3 style={{ fontSize: "16px", marginBottom: "10px", textAlign: "center" }}>Vital Metrics</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={barData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                        <Bar dataKey="value" fill="#8884d8" name="Patient Value" />
                        <Bar dataKey="normal" fill="#82ca9d" name="Normal Ref" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Radar Chart */}
            <div style={{ flex: "1 1 300px", minWidth: "300px", height: "300px", background: "#fff", padding: "10px", borderRadius: "10px", boxShadow: "0 2px 10px rgba(0,0,0,0.1)" }}>
                <h3 style={{ fontSize: "16px", marginBottom: "10px", textAlign: "center" }}>Health Profile</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="name" />
                        <PolarRadiusAxis />
                        <Radar name="Patient" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                        <Legend />
                        <Tooltip />
                    </RadarChart>
                </ResponsiveContainer>
            </div>

        </div>
    );
};

export default HealthCharts;
