function DashboardCard({ title, value }) {
  return (
    <div style={{
      background: "#fff",
      padding: "20px",
      borderRadius: "10px",
      width: "200px",
      boxShadow: "0 0 10px rgba(0,0,0,0.1)"
    }}>
      <h4>{title}</h4>
      <p style={{ fontSize: "20px", fontWeight: "bold" }}>{value}</p>
    </div>
  );
}

export default DashboardCard;
