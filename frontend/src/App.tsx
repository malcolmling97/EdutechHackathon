import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import DashboardView from './views/DashboardView';
import ChatView from './views/ChatView';
import StudyView from './views/StudyView';
import QuizView from './views/QuizView';
import NotesView from './views/NotesView';
import StudyGuideView from './views/StudyGuideView';
import FlashcardsView from './views/FlashcardsView';
import OpenEndedView from './views/OpenEndedView';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardView />} />
          <Route path="/chat/:id" element={<ChatView />} /> {/* Accepts dynamic ID */}
          <Route path="/study" element={<StudyView />} />
          <Route path="/quiz" element={<QuizView />} />
          <Route path="/notes" element={<NotesView />} />
          <Route path ="/study-guide/content" element={<StudyGuideView/>}/>
          <Route path="/flashcards" element={<FlashcardsView />} />
          <Route path="/open-ended" element={<OpenEndedView />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App; 