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
          <Route path="/study/:id" element={<StudyView />} />
          <Route path="/quiz/:id" element={<QuizView />} />
          <Route path="/notes/:id" element={<NotesView />} />
          <Route path ="/study-guide/content/:id" element={<StudyGuideView/>}/>
          <Route path="/flashcards/:id" element={<FlashcardsView />} />
          <Route path="/open-ended/:id" element={<OpenEndedView />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App; 