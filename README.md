# Healthcare-Prediction-System
Ml based Health prediction

Project Overview & Workflow
1. System Architecture
This is a Healthcare Prediction System consisting of:

Frontend: React.js (Vite)
Backend: Python (Flask)
Database: PostgreSQL (via SQLAlchemy)
Machine Learning: Scikit-Learn (Random Forest Models)
2. Work Flow
User Entry: Users land on 
Landing.jsx
, then Login/Signup.
Authentication: 
Login.jsx
 sends credentials to backend 
app.py
. JWT token is returned.
Dashboard: User views health stats (
Dashboard.jsx
), visualizes data (
HealthCharts.jsx
).
Prediction:
User goes to 
Diabetes.jsx
 or 
Heart.jsx
.
Enters data (or uploads PDF report).
app.py
 receives data -> 
health_utils.py
 imputes missing values -> Model predicts risk.
Result displayed to user.
Reports & Appointments:
System generates PDF reports (
report_generator.py
).
Emails them (
email_service.py
).
User can book appointments (
Booking.jsx
, 
Hospitals.jsx
).
3. File Descriptions
Backend (/backend)
File	Purpose
app.py	Main Entry Point. Handles API routes, DB connections, and model serving.
models.py	Database Schema (User, Doctor, Appointment, Report, etc.).
health_utils.py	Logic Core. Contains Smart Imputation estimates and Risk Logic.
report_generator.py	Creates PDF medical reports using reportlab.
email_service.py	Handles sending emails (OTP, Reports, Appointments).
pdf_utils.py	Extracts text/data from uploaded patient PDF reports.
otp_utils.py	Helper functions for generating/verifying OTPs.
models/ (Directory)	Contains trained ML models (.pkl) and scalers.
Frontend (/frontend/src)
Pages (/pages)
File	Purpose
Login.jsx / Signup.jsx	User authentication pages.
OtpVerify.jsx	OTP verification page (features glassmorphism style).
Dashboard.jsx	Main patient hub. Shows charts and quick links.
Diabetes.jsx / Heart.jsx	Prediction Forms. Inputs for health data.
DoctorDashboard.jsx	Interface for doctors to view appointments/chats.
Booking.jsx	Appointment booking interface.
Hospitals.jsx	List of hospitals/doctors via Google Maps integration (if active).
ChatWindow.jsx	Real-time chat between Patient and Doctor.
Components (/components)
File	Purpose
Sidebar.jsx	Navigation menu.
HealthCharts.jsx	Visualization of patient health trends (Chart.js).
4. Key Features
Smart Imputation: If users miss fields (e.g., Insulin), the system estimates them based on other inputs (e.g., Glucose) to Ensure accurate ML predictions.
Glassmorphism UI: Modern UI design applied to Login/OTP pages.
Real-time Chat: Socket.IO enabled chat.
