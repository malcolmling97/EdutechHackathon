import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import DashboardView from './views/DashboardView';
import ChatView from './views/ChatView';
import QuizView from './views/QuizView';
import NotesView from './views/NotesView';
import StudyGuideView from './views/StudyGuideView';
import FlashcardsView from './views/FlashcardsView';
import OpenEndedView from './views/OpenEndedView';
import StudyOptionsView from './views/StudyOptionView';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardView />} />
          <Route path="/chat/:id" element={<ChatView />} />
          <Route path="/notes/:id" element={<NotesView />} />
          <Route path="/study/:spaceId" element={<StudyOptionsView />} />
          <Route path="/study/:spaceId/flashcards" element={<FlashcardsView />} />
          <Route path="/study/:spaceId/quiz" element={<QuizView />} />
          <Route path="/study/:spaceId/openended" element={<OpenEndedView />} />
          <Route path="/study/:spaceId/studyguide" element={<StudyGuideView />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App; 