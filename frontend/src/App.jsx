import { Navigate, Route, Routes } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Landing from "./pages/Landing";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Register />} />
      <Route path="/create" element={<Navigate to="/signup" replace />} />
      <Route path="/signin" element={<Navigate to="/login" replace />} />
      <Route path="/register" element={<Navigate to="/signup" replace />} />
      <Route path="/create-account" element={<Navigate to="/signup" replace />} />
      <Route path="/landing" element={<Landing />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

