import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api";

export default function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  async function handleLogin(e) {
    e.preventDefault();

    try {
      const response = await api.post("/auth/login", {
        email,
        password
      });

      // Save user session
      localStorage.setItem("user", JSON.stringify(response.data.user));

      navigate("/dashboard");
    } catch (error) {
      setMessage("Invalid email or password");
    }
    
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2>Login</h2>

        <form onSubmit={handleLogin}>
          <input
            style={styles.input}
            type="email"
            placeholder="Email"
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            style={styles.input}
            type="password"
            placeholder="Password"
            onChange={(e) => setPassword(e.target.value)}
          />

          <button style={styles.button}>Login</button>
        </form>

        {message && <p style={{ color: "red" }}>{message}</p>}

        <p style={{ marginTop: "10px", fontSize: "14px" }}>
          Don't have an account?{" "}
          <span
            style={{
              color: "#4A90E2",
              cursor: "pointer",
              textDecoration: "none",
            }}
            onClick={() => navigate("/register")}
          >
            Register here
          </span>
        </p>

      </div>
    </div>
  );
}

const styles = {
  container: {
    background: "#eef2f3",
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  card: {
    background: "#fff",
    padding: "30px",
    width: "300px",
    borderRadius: "12px",
    boxShadow: "0px 4px 12px rgba(0,0,0,0.1)",
  },
  input: {
    width: "100%",
    marginBottom: "12px",
    padding: "10px",
    borderRadius: "6px",
    border: "1px solid #ccc",
  },
  button: {
    width: "100%",
    padding: "12px",
    background: "#4A90E2",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "bold",
  },
};
