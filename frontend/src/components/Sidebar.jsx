import { useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Activity,
  Heart,
  Calendar,
  MessageSquare,
  Users,
  HelpCircle,
  Settings,
  LogOut
} from "lucide-react";

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("firstName");
    localStorage.removeItem("lastName");
    navigate("/login");
  };

  const menuItems = [
    { title: "Overview", icon: <LayoutDashboard size={20} />, path: "/dashboard" },
    { title: "Diabetes", icon: <Activity size={20} />, path: "/diabetes" },
    { title: "Heart Health", icon: <Heart size={20} />, path: "/heart" },
    { title: "Appointment", icon: <Calendar size={20} />, path: "/appointments" },
    { title: "Message", icon: <MessageSquare size={20} />, path: "/messages" },
    { title: "Community", icon: <Users size={20} />, path: "/community" },
  ];

  return (
    <div style={{
      width: "250px",
      background: "#ffffff",
      padding: "20px",
      height: "100vh",
      display: "flex",
      flexDirection: "column",
      borderRight: "1px solid #e0e0e0"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "40px" }}>
        <div style={{
          width: "40px", height: "40px", borderRadius: "50%", background: "#e0f2f1",
          display: "flex", alignItems: "center", justifyContent: "center"
        }}>
          <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSR8QDbNkhSgU66jWBkUK24Ckw-9pgkBkmG8g&s" alt="Logo" width="40" style={{ borderRadius: "50%" }} />
        </div>
        <div>
          <h3 style={{ margin: 0, fontSize: "18px", color: "#333" }}>HealthCare</h3>
          <p style={{ margin: 0, fontSize: "10px", color: "#888" }}>Diagnosis</p>
        </div>
      </div>

      <p style={{ fontSize: "12px", color: "#888", marginBottom: "10px" }}>Menu</p>

      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {menuItems.map((item) => (
          <li key={item.title} style={{ marginBottom: "10px" }}>
            <div
              onClick={() => navigate(item.path)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "10px 15px",
                borderRadius: "10px",
                cursor: "pointer",
                background: location.pathname === item.path ? "#00c853" : "transparent",
                color: location.pathname === item.path ? "#fff" : "#666",
                fontWeight: location.pathname === item.path ? "600" : "400",
                transition: "all 0.3s"
              }}
            >
              {item.icon}
              <span>{item.title}</span>
            </div>
          </li>
        ))}
      </ul>

      <div style={{ marginTop: "auto" }}>
        <p style={{ fontSize: "12px", color: "#888", marginBottom: "10px" }}>Help & Settings</p>
        <ul style={{ listStyle: "none", padding: 0 }}>
          <li style={{ marginBottom: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "10px", color: "#666", cursor: "pointer" }}>
              <Users size={20} />
              <span>Referrals</span>
            </div>
          </li>
          <li style={{ marginBottom: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "10px", color: "#666", cursor: "pointer" }}>
              <HelpCircle size={20} />
              <span>Help</span>
            </div>
          </li>
          <li>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "10px", color: "#666", cursor: "pointer" }}>
              <Settings size={20} />
              <span>Settings</span>
            </div>
          </li>
          <li>
            <div onClick={handleLogout} style={{ display: "flex", alignItems: "center", gap: "12px", padding: "10px", color: "red", cursor: "pointer" }}>
              <LogOut size={20} />
              <span>Logout</span>
            </div>
          </li>
        </ul>

        {/* Subscription Alert Card */}
        <div style={{
          background: "#f4f6f8",
          padding: "15px",
          borderRadius: "15px",
          marginTop: "20px"
        }}>
          <h4 style={{ margin: "0 0 5px 0", fontSize: "14px" }}>Alert!</h4>
          <p style={{ margin: "0 0 10px 0", fontSize: "11px", color: "#666" }}>Your subscription will expire soon...</p>
          <div style={{ display: "flex", gap: "10px" }}>
            <button style={{
              background: "#00c853", border: "none", color: "white",
              padding: "5px 15px", borderRadius: "8px", fontSize: "12px", cursor: "pointer"
            }}>Renew</button>
            <button style={{
              background: "white", border: "1px solid #ddd", color: "#333",
              padding: "5px 15px", borderRadius: "8px", fontSize: "12px", cursor: "pointer"
            }}>Renew</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
