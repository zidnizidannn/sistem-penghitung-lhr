import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Index from './pages';
import Dashboard from './pages/dashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<Index/>}></Route>
        <Route path='/dashboard' element={<Dashboard/>}></Route>
      </Routes>
    </Router>
  );
}

export default App;
