import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Main from "./pages/main";
import Dashboard from "./pages/dashboard";
import History from "./pages/history";
import LiveDetection from "./pages/live";
import DataLHR from "./pages/data-lhr";

function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<Main/>}></Route>
        <Route path='/dashboard' element={<Dashboard/>}></Route>
        <Route path='/history' element={<History/>}></Route>
        <Route path='/live' element={<LiveDetection/>}></Route>
        <Route path='/data-lhr' element={<DataLHR/>}></Route>
      </Routes>
    </Router>
  );
}

export default App;