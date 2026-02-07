import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    const response = await fetch("http://127.0.0.1:5001/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("isLoggedIn", "true");
      localStorage.setItem("firstName", data.user.first_name);
      localStorage.setItem("lastName", data.user.last_name);
      localStorage.setItem("email", data.user.email);
      localStorage.setItem("role", data.user.role);
      navigate(data.user.role === "doctor" ? "/doctor-dashboard" : "/dashboard");
    } else {
      alert(data.error);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "50px auto" }}>
      <h2>Login</h2>

      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
          required
        />

        <button type="submit" style={{ width: "100%", padding: "10px" }}>
          Login
        </button>
      </form>

      <p style={{ marginTop: "10px" }}>
        Don’t have an account? <a href="/signup">Sign up</a>
      </p>
    </div>
  );
}

export default Login;
