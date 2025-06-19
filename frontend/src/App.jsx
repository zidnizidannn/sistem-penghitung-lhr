import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Main from "./pages/main";
import Dashboard from "./pages/dashboard";
import History from "./pages/history";
import LiveDetection from "./pages/live";
import DataLHR from "./pages/data-lhr";

function App() {
  const ProtectedRoute = ({ children }) => {
    const token = localStorage.getItem('token');
    return token ? children : <Navigate to="/" replace />;
  };
  return (
    <Router>
      <Routes>
        <Route path='/' element={<Main/>}></Route>

        <Route 
        path='/dashboard' 
        element={
          <ProtectedRoute>
            <Dashboard/>
          </ProtectedRoute>}/>
        <Route 
        path='/history' 
        element={
          <ProtectedRoute>
            <History/>
          </ProtectedRoute>}/>
        <Route 
        path='/live' 
        element={
          <ProtectedRoute>
            <LiveDetection/>
          </ProtectedRoute>}/>
        <Route 
        path='/data-lhr' 
        element={
          <ProtectedRoute>
            <DataLHR/>
          </ProtectedRoute>}/>
      </Routes>
    </Router>
  );
}

export default App;