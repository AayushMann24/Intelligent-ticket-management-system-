import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import TicketsPage from "./pages/TicketsPage";
import UsersPage from "./pages/UsersPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import AssistantPage from "./pages/AssistantPage";
import SettingsPage from "./pages/SettingsPage";
function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public Pages */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected Pages */}
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/tickets" element={<TicketsPage />} />
        <Route path="/users" element={<UsersPage />} />

        {/* Default */}
        <Route path="*" element={<Navigate to="/" />}/>

        <Route path="/analytics" element={<AnalyticsPage />} />

        <Route path="/assistant" element={<AssistantPage />} />

        <Route path="/settings" element={<SettingsPage />} />
        <Route
          path="/users"
          element={<UsersPage />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;