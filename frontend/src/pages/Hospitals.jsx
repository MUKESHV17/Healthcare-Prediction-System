import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { Search, MapPin, Navigation } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";

// Fix for default marker icon in Leaflet
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

let DefaultIcon = L.icon({
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

function Hospitals() {
    const navigate = useNavigate();
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const recommendedDept = queryParams.get("department") || "";

    const [position, setPosition] = useState([19.0760, 72.8777]); // Mumbai default
    const [hospitals, setHospitals] = useState([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedDept, setSelectedDept] = useState(recommendedDept);
    const [userPincode, setUserPincode] = useState(null);

    // Map Updater Component to center map
    function MapUpdater({ center }) {
        const map = useMap();
        useEffect(() => {
            map.flyTo(center, 13);
        }, [center]);
        return null;
    }

    useEffect(() => {
        // 1. Fetch User Profile for Pincode
        const email = localStorage.getItem("email");
        if (email) {
            fetch(`http://127.0.0.1:5001/api/user/profile?email=${email}`)
                .then(res => res.json())
                .then(data => {
                    if (data.pincode) {
                        setUserPincode(data.pincode);
                        // 2. Geocode Pincode
                        fetch(`https://nominatim.openstreetmap.org/search?format=json&postalcode=${data.pincode}&country=India`)
                            .then(res => res.json())
                            .then(geo => {
                                if (geo && geo.length > 0) {
                                    const lat = parseFloat(geo[0].lat);
                                    const lon = parseFloat(geo[0].lon);
                                    setPosition([lat, lon]);
                                    fetchHospitals(lat, lon);
                                } else {
                                    // Fallback if geocoding fails, just fetch all
                                    fetchHospitals();
                                }
                            });
                    } else {
                        fetchHospitals();
                    }
                })
                .catch(() => fetchHospitals());
        } else {
            fetchHospitals();
        }
    }, [selectedDept]);

    const fetchHospitals = async (lat = null, lng = null, query = "") => {
        let url = `http://127.0.0.1:5001/hospitals?department=${selectedDept || ""}&search=${query}`;
        if (lat && lng) {
            url += `&lat=${lat}&lng=${lng}`; // Send for sorting/distance calc
        }

        try {
            const res = await fetch(url);
            const data = await res.json();
            setHospitals(data);

            // If data found and user has no specific location (or search mode), fly to first result
            if (data.length > 0 && query) {
                setPosition([data[0].lat, data[0].lng]);
            }
        } catch (err) {
            console.error(err);
        }
    };

    // Debounced search effect
    useEffect(() => {
        const timer = setTimeout(() => {
            if (position) {
                fetchHospitals(position[0], position[1], searchQuery);
            } else {
                fetchHospitals(null, null, searchQuery);
            }
        }, 500);
        return () => clearTimeout(timer);
    }, [searchQuery, selectedDept]); // Trigger on search or dept change

    return (
        <div style={{ display: "flex", height: "100vh", background: "#f8fafc" }}>
            <Sidebar />
            <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
                {/* Header-like search bar */}
                <div style={{ padding: "20px", display: "flex", gap: "20px", background: "white", borderBottom: "1px solid #eee", alignItems: "center" }}>
                    <div style={{ flex: 1, position: "relative" }}>
                        <Search size={18} style={{ position: "absolute", left: "12px", top: "12px", color: "#888" }} />
                        <input
                            type="text"
                            placeholder="Search city, district, or hospital..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            style={{ width: "100%", padding: "10px 10px 10px 40px", borderRadius: "10px", border: "1px solid #ddd", outline: "none" }}
                        />
                    </div>
                    <select
                        value={selectedDept}
                        onChange={(e) => setSelectedDept(e.target.value)}
                        style={{ padding: "10px", borderRadius: "10px", border: "1px solid #ddd" }}
                    >
                        <option value="">All Departments</option>
                        <option value="Cardiology">Cardiology</option>
                        <option value="Endocrinology">Endocrinology</option>
                        <option value="General">General</option>
                        <option value="Pediatrics">Pediatrics</option>
                        <option value="Neurology">Neurology</option>
                        <option value="Orthopedics">Orthopedics</option>
                    </select>
                </div>

                <div style={{ flex: 1, position: "relative" }}>
                    <MapContainer center={position} zoom={10} style={{ height: "100%", width: "100%" }}>
                        <MapUpdater center={position} />
                        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

                        {/* Current Location Marker */}
                        <Marker position={position}>
                            <Popup>
                                <strong>You are here</strong><br />
                                Pincode: {userPincode || "N/A"}
                            </Popup>
                        </Marker>

                        {/* 50km Highlighting Circle (Optional visual aid) */}
                        <Circle
                            center={position}
                            radius={50010}
                            pathOptions={{ color: 'blue', fillColor: 'blue', fillOpacity: 0.05 }}
                        />

                        {/* Hospital Markers */}
                        {hospitals.map(h => (
                            <Marker key={h.id} position={[h.lat, h.lng]}>
                                <Popup>
                                    <div style={{ minWidth: "200px" }}>
                                        <h4 style={{ margin: "0 0 5px 0" }}>{h.name}</h4>
                                        <p style={{ margin: "0 0 10px 0", fontSize: "12px", color: "#666" }}>{h.address}</p>
                                        {h.distance && <p style={{ fontSize: "11px", color: "blue" }}>{h.distance} km away</p>}
                                        <div style={{ display: "flex", flexWrap: "wrap", gap: "5px", marginBottom: "10px" }}>
                                            {h.departments.map(d => (
                                                <span key={d} style={{ background: "#e8f5e9", color: "#2e7d32", fontSize: "10px", padding: "2px 6px", borderRadius: "5px" }}>{d}</span>
                                            ))}
                                        </div>
                                        <button
                                            onClick={() => navigate(`/booking?hospital_id=${h.id}&department=${selectedDept}`)}
                                            style={{ width: "100%", background: "#00c853", color: "white", border: "none", padding: "8px", borderRadius: "8px", cursor: "pointer" }}
                                        >
                                            View Doctors & Book
                                        </button>
                                    </div>
                                </Popup>
                            </Marker>
                        ))}
                    </MapContainer>
                </div>
            </div>
        </div>
    );
}

export default Hospitals;
