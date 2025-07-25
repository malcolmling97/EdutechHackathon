import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import DashboardView from './views/DashboardView';
import ChatView from './views/ChatView';
import StudyView from './views/StudyView';
import QuizView from './views/QuizView';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardView />} />
          <Route path="/chat/:id" element={<ChatView />} /> {/* Accepts dynamic ID */}
          <Route path="/study" element={<StudyView />} />
          <Route path="/quiz" element={<QuizView />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App; 