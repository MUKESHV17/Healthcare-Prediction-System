import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import "./Profile.css";
import { Camera } from "lucide-react";

function Profile() {
    const [user, setUser] = useState({
        firstName: "",
        lastName: "",
        email: "",
        phone: "",
        city: "",
        dob: "",
        pincode: "",
        address: "",
        age: "",
        weight: "",
        height: "",
        profilePic: "",
        gender: "Male"
    });

    const [passwords, setPasswords] = useState({
        currentPassword: "",
        newPassword: "",
        confirmPassword: ""
    });

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const email = localStorage.getItem("email");

    useEffect(() => {
        const fetchUser = async () => {
            try {
                // Fixed logic to use /api/user/profile as implemented in backend
                const response = await fetch(`http://127.0.0.1:5001/api/user/profile?email=${email}`);
                const data = await response.json();
                if (response.ok) {
                    setUser(prev => ({ ...prev, ...data }));
                } else {
                    setError(data.error);
                }
            } catch {
                setError("Failed to fetch profile");
            }
        };

        if (email) {
            fetchUser();
        }
    }, [email]);

    const handleChange = (e) => {
        setUser({ ...user, [e.target.name]: e.target.value });
    };

    const handlePasswordChange = (e) => {
        setPasswords({ ...passwords, [e.target.name]: e.target.value });
    };

    const [tempImage, setTempImage] = useState(null);
    const [cropAlign, setCropAlign] = useState("center"); // top, center, bottom

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setTempImage(reader.result);
                // Default process with center alignment
                processImage(reader.result, "center");
            };
            reader.readAsDataURL(file);
        }
    };

    const processImage = (imgSrc, alignment) => {
        setCropAlign(alignment);
        const img = new Image();
        img.src = imgSrc;
        img.onload = () => {
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");

            // Set canvas to square (min dimension)
            const minDim = Math.min(img.width, img.height);
            canvas.width = minDim;
            canvas.height = minDim;

            // Calculate source coordinates based on alignment
            let sx = 0, sy = 0;
            if (img.width > img.height) {
                // Landscape: Center horizontally
                sx = (img.width - img.height) / 2;
            } else {
                // Portrait: Adjust based on user choice
                if (alignment === "top") sy = 0;
                else if (alignment === "center") sy = (img.height - img.width) / 2;
                else if (alignment === "bottom") sy = img.height - img.width;
            }

            ctx.drawImage(img, sx, sy, minDim, minDim, 0, 0, minDim, minDim);
            setUser(prev => ({ ...prev, profilePic: canvas.toDataURL() }));
        };
    };

    const handleSaveProfile = async () => {
        try {
            // Fixed logic to use /api/user/profile as implemented in backend
            const response = await fetch("http://127.0.0.1:5001/api/user/profile", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ...user, email })
            });
            const data = await response.json();
            if (response.ok) {
                setMessage("Profile updated successfully!");
                // Update local storage names if changed
                localStorage.setItem("firstName", user.firstName);
                localStorage.setItem("lastName", user.lastName);
                setTimeout(() => setMessage(""), 3000);
            } else {
                setError(data.error);
                setTimeout(() => setError(""), 3000);
            }
        } catch {
            setError("Failed to update profile");
        }
    };

    const handleChangePassword = async () => {
        if (passwords.newPassword !== passwords.confirmPassword) {
            setError("New passwords do not match");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5001/change-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: user.email,
                    currentPassword: passwords.currentPassword,
                    newPassword: passwords.newPassword
                })
            });
            const data = await response.json();
            if (response.ok) {
                setMessage("Password changed successfully");
                setPasswords({ currentPassword: "", newPassword: "", confirmPassword: "" });
                setTimeout(() => setMessage(""), 3000);
            } else {
                setError(data.error);
                setTimeout(() => setError(""), 3000);
            }
        } catch {
            setError("Failed to change password");
        }
    };

    return (
        <div className="profile-container">
            <Sidebar />
            <div className="profile-main">
                <div className="profile-header">
                    <h2>My Profile</h2>
                </div>

                {message && <div style={{ marginBottom: "20px", color: "green", fontWeight: "bold" }}>{message}</div>}
                {error && <div style={{ marginBottom: "20px", color: "red", fontWeight: "bold" }}>{error}</div>}

                <div className="profile-content">
                    {/* Left Column */}
                    <div className="profile-left">
                        <div className="avatar-card">
                            <div className="avatar-wrapper">
                                <img
                                    src={user.profilePic || "https://randomuser.me/api/portraits/men/32.jpg"}
                                    alt="Profile"
                                    className="profile-avatar"
                                />
                            </div>

                            {tempImage && (
                                <div style={{ marginBottom: "15px", display: "flex", justifyContent: "center", gap: "5px" }}>
                                    <button
                                        type="button"
                                        onClick={() => processImage(tempImage, "top")}
                                        style={{
                                            fontSize: "10px", padding: "4px 8px", borderRadius: "4px", border: "1px solid #ddd",
                                            background: cropAlign === "top" ? "#00c853" : "white", color: cropAlign === "top" ? "white" : "#333", cursor: "pointer"
                                        }}
                                    >
                                        Top
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => processImage(tempImage, "center")}
                                        style={{
                                            fontSize: "10px", padding: "4px 8px", borderRadius: "4px", border: "1px solid #ddd",
                                            background: cropAlign === "center" ? "#00c853" : "white", color: cropAlign === "center" ? "white" : "#333", cursor: "pointer"
                                        }}
                                    >
                                        Center
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => processImage(tempImage, "bottom")}
                                        style={{
                                            fontSize: "10px", padding: "4px 8px", borderRadius: "4px", border: "1px solid #ddd",
                                            background: cropAlign === "bottom" ? "#00c853" : "white", color: cropAlign === "bottom" ? "white" : "#333", cursor: "pointer"
                                        }}
                                    >
                                        Bottom
                                    </button>
                                </div>
                            )}

                            <label className="upload-btn">
                                <Camera size={16} style={{ marginBottom: "-3px", marginRight: "5px" }} />
                                Change Photo
                                <input type="file" hidden accept="image/*" onChange={handleFileChange} />
                            </label>
                        </div>

                        <div className="password-card">
                            <h3>Change Password</h3>
                            <input
                                type="password"
                                name="currentPassword"
                                placeholder="Current Password"
                                className="password-input"
                                value={passwords.currentPassword}
                                onChange={handlePasswordChange}
                            />
                            <input
                                type="password"
                                name="newPassword"
                                placeholder="New Password"
                                className="password-input"
                                value={passwords.newPassword}
                                onChange={handlePasswordChange}
                            />
                            <input
                                type="password"
                                name="confirmPassword"
                                placeholder="Confirm Password"
                                className="password-input"
                                value={passwords.confirmPassword}
                                onChange={handlePasswordChange}
                            />
                            <button className="password-btn" onClick={handleChangePassword}>Update Password</button>
                        </div>
                    </div>

                    {/* Right Column */}
                    <div className="details-card">
                        <h3>Personal Details</h3>
                        <div className="profile-form-grid">
                            <div className="profile-form-group">
                                <label>First Name</label>
                                <input name="firstName" value={user.firstName || ""} onChange={handleChange} />
                            </div>
                            <div className="profile-form-group">
                                <label>Last Name</label>
                                <input name="lastName" value={user.lastName || ""} onChange={handleChange} />
                            </div>
                            <div className="profile-form-group full-width">
                                <label>Email</label>
                                <input value={user.email || ""} disabled />
                            </div>
                            <div className="profile-form-group">
                                <label>Phone</label>
                                <input name="phone" value={user.phone || ""} onChange={handleChange} />
                            </div>
                            <div className="profile-form-group">
                                <label>Date of Birth</label>
                                <input type="date" name="dob" value={user.dob || ""} onChange={handleChange} />
                            </div>
                            <div className="profile-form-group">
                                <label>Age</label>
                                <input type="number" name="age" value={user.age || ""} onChange={handleChange} />
                            </div>
                            <div className="profile-form-group">
                                <label>Gender</label>
                                <select name="gender" value={user.gender || "Male"} onChange={handleChange} className="profile-select">
                                    <option value="Male">Male</option>
                                    <option value="Female">Female</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>
                            <div className="profile-form-group">
                                <label>Height (cm)</label>
                                <input type="number" name="height" value={user.height || ""} onChange={handleChange} />
                            </div>
                            <div className="profile-form-group">
                                <label>Weight (kg)</label>
                                <input type="number" name="weight" value={user.weight || ""} onChange={handleChange} />
                            </div>
                            <div className="profile-form-group full-width">
                                <label>Address</label>
                                <input name="address" value={user.address || ""} onChange={handleChange} placeholder="Street Address" />
                            </div>
                            <div className="profile-form-group">
                                <label>City</label>
                                <input name="city" value={user.city || ""} onChange={handleChange} />
                            </div>
                            <div className="profile-form-group">
                                <label>Pincode</label>
                                <input name="pincode" value={user.pincode || ""} onChange={handleChange} />
                            </div>
                        </div>
                        <button className="save-btn" onClick={handleSaveProfile}>Save Changes</button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Profile;
