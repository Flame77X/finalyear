import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import InterviewPage from './pages/InterviewPage';
import CandidateLogin from './pages/CandidateLogin';
import LandingPage from './pages/LandingPage';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/candidate-login" element={<CandidateLogin />} />
                <Route path="/interview" element={<InterviewPage />} />
            </Routes>
        </Router>
    );
}

export default App;
