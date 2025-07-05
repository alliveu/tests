import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SignupPage from './pages/SignupPage';
import LoginPage from './pages/LoginPage';
import Chatbot from './components/Chatbot';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <div className="p-4 flex flex-col items-center gap-4">
              <h1 className="text-2xl font-bold">사이버불링 신고 웹에 오신 걸 환영합니다.</h1>
              <p>로그인 또는 회원가입을 진행해주세요.</p>
              <div className="flex gap-4">
                <a href="/login" className="bg-green-500 text-white px-4 py-2 rounded">로그인</a>
                <a href="/signup" className="bg-blue-500 text-white px-4 py-2 rounded">회원가입</a>
              </div>
            </div>
          }
        />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/chat" element={<Chatbot />} />
        <Route path="*" element={<div className="p-4">404 페이지를 찾을 수 없습니다.</div>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

