import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Index from './pages';
import Dashboard from './pages/dashboard';
import History from './pages/history';

function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<Index/>}></Route>
        <Route path='/dashboard' element={<Dashboard/>}></Route>
        <Route path='/history' element={<History/>}></Route>
      </Routes>
    </Router>
  );
}

export default App;
