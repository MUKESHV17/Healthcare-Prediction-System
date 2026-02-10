import React from "react";
import { useNavigate } from "react-router-dom";
import "./Landing.css";

const Landing = () => {
    const navigate = useNavigate();

    return (
        <div className="landing-container">
            {/* Navbar */}
            <nav className="landing-navbar">
                <div className="logo-section">
                    <img
                        src="https://w7.pngwing.com/pngs/525/904/png-transparent-logo-health-health-leaf-photography-logo-thumbnail.png"
                        alt="MedPro Logo"
                        className="logo-image"
                    />
                    <h1 className="logo-text">MedPro</h1>
                </div>
                <div className="auth-buttons">
                    <button className="btn-login" onClick={() => navigate("/login")}>
                        Login
                    </button>
                    <button className="btn-signup" onClick={() => navigate("/signup")}>
                        Sign Up
                    </button>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="hero-section">
                <div className="hero-content">
                    <h1 className="hero-title">
                        Your Health, <span className="highlight">Our Priority</span>
                    </h1>
                    <p className="hero-description">
                        Experience the future of healthcare management. Track your vitals,
                        schedule appointments, and predict health risks with our advanced
                        AI-powered platform.
                    </p>
                    <button className="cta-button" onClick={() => navigate("/signup")}>
                        Get Started
                    </button>
                </div>
            </main>
        </div>
    );
};

export default Landing;
