import Sidebar from "../components/Sidebar";
import DashboardCard from "../components/DashboardCard";

function Dashboard() {
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />

      <div style={{ padding: "20px", flex: 1 }}>
        <h2>Hi 👋 Welcome Back</h2>
        <p>Check your health status</p>

        <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
          <DashboardCard title="Diabetes Risk" value="Check Now" />
          <DashboardCard title="Heart Health" value="Check Now" />
          <DashboardCard title="Reports" value="Coming Soon" />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
