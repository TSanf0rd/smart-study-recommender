import React from "react"
import { Routes, Route } from "react-router-dom";
import DashboardLayout from "./DashboardLayout";
import LoginPage from "./LoginPage";
import RegisterPage from "./RegisterPage";
import Dashboard from "./Dashboard";
import Videos from "./Videos";

function App() {
  return (
    <Routes>
      {/* Public route */}
      <Route path="/" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected layout */}
      <Route element={<DashboardLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/videos" element={<Videos />} />
      </Route>
    </Routes>
  )
}

export default App
