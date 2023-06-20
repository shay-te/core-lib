import { BrowserRouter, Route, Routes, useNavigate } from 'react-router-dom';

import './App.scss';
import Generator from './pages/generator';
import Main from './pages/generate';


const App = () => {
  return (
      <BrowserRouter>
        <Routes>
          <Route path={'/'} element={<Main />} />
          <Route path={'/generator'} element={<Generator />} />
        </Routes>
      </BrowserRouter>
  );
}

export default App;