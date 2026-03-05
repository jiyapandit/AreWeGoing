import { Navigate, Route, Routes } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Landing from "./pages/Landing";
import CreateGroup from "./pages/CreateGroup";
import JoinGroup from "./pages/JoinGroup";
import GroupDashboard from "./pages/GroupDashboard";

function isAuthenticated() {
  const localToken = window.localStorage.getItem("arewegoing_access_token");
  const sessionToken = window.sessionStorage.getItem("arewegoing_access_token");
  return Boolean(localToken || sessionToken);
}

function ProtectedRoute({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/landing" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Register />} />
      <Route path="/create" element={<Navigate to="/signup" replace />} />
      <Route path="/signin" element={<Navigate to="/login" replace />} />
      <Route path="/register" element={<Navigate to="/signup" replace />} />
      <Route path="/create-account" element={<Navigate to="/signup" replace />} />
      <Route path="/landing" element={<Landing />} />
      <Route
        path="/create-group"
        element={
          <ProtectedRoute>
            <CreateGroup />
          </ProtectedRoute>
        }
      />
      <Route path="/join-group" element={<JoinGroup />} />
      <Route
        path="/groups/:groupId"
        element={
          <ProtectedRoute>
            <GroupDashboard />
          </ProtectedRoute>
        }
      />
      <Route path="/join" element={<Navigate to="/join-group" replace />} />
      <Route path="/create-group-room" element={<Navigate to="/create-group" replace />} />
      <Route path="*" element={<Navigate to="/landing" replace />} />
    </Routes>
  );
}
