import { useNavigate } from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    navigate("/login");
  };

  return (
    <div style={{
      width: "220px",
      background: "#f4f6f8",
      padding: "20px",
      height: "100vh"
    }}>
      <h3>Healthcare</h3>

      <ul style={{ listStyle: "none", padding: 0 }}>
        <li><a href="/dashboard">🏠 Dashboard</a></li>
        <li><a href="/diabetes">🩸 Diabetes</a></li>
        <li><a href="/heart">❤️ Heart Disease</a></li>
        <li>
          <button onClick={handleLogout} style={{
            background: "none",
            border: "none",
            color: "red",
            cursor: "pointer",
            padding: 0
          }}>
            🚪 Logout
          </button>
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;
