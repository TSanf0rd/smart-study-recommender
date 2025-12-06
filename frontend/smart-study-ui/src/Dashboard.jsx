import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));

  useEffect(() => {
    if (!user) {
      navigate("/");
    }
  }, [user, navigate]);

  // While redirecting, render nothing
  if (!user) return null;

  return (
    <div style={styles.dashboard}>
      {/* Sidebar */}
      <div style={styles.sidebar}>
        <h2 style={styles.logo}>SmartStudy</h2>

        <button style={styles.menuItem}>Home</button>
        <button style={styles.menuItem}>Resources</button>
        <button style={styles.menuItem}>Profile</button>

        <button
          style={styles.logout}
          onClick={() => {
            localStorage.removeItem("user");
            navigate("/");
          }}
        >
          Logout
        </button>
      </div>

      {/* Main Content */}
      <div style={styles.content}>
        <h1>Welcome, {user.username} 👋</h1>
        <p>Your role: {user.role}</p>
        <p>Account created: {user.created_at}</p>
      </div>
    </div>
  );
}

const styles = {
  dashboard: {
    display: "flex",
    height: "100vh",
  },
  sidebar: {
    width: "240px",
    background: "#2E3A59",
    color: "white",
    padding: "20px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
  },
  logo: {
    textAlign: "center",
  },
  menuItem: {
    background: "transparent",
    color: "white",
    border: "none",
    padding: "12px",
    textAlign: "left",
    cursor: "pointer",
    fontSize: "16px",
  },
  logout: {
    background: "#FF6B6B",
    padding: "12px",
    borderRadius: "6px",
    border: "none",
    color: "white",
    cursor: "pointer",
  },
  content: {
    flex: 1,
    padding: "40px",
    background: "#F7F9FC",
  },
};
