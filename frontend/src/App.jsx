import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100">
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
