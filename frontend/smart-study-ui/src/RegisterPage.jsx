import React, { useState } from "react";
import api from "./api";

export default function RegisterPage() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    role: "student",
  });

  const [message, setMessage] = useState("");

  async function handleRegister(e) {
    e.preventDefault();

    try {
      await api.post("/auth/register", form);
      setMessage("User registered successfully!");
    } catch (error) {
      setMessage(error.response?.data?.detail || "Registration failed");
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2>Create Account</h2>

        <form onSubmit={handleRegister}>
          <input
            style={styles.input}
            placeholder="Username"
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />

          <input
            style={styles.input}
            type="email"
            placeholder="Email"
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />

          <input
            style={styles.input}
            type="password"
            placeholder="Password"
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />

          <select
            style={styles.input}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
          >
            <option value="student">Student</option>
            <option value="instructor">Instructor</option>
            <option value="tutor">Tutor</option>
          </select>

          <button style={styles.button}>Register</button>
        </form>

        {message && <p>{message}</p>}
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
    width: "320px",
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
    background: "green",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },
};
