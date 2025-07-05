import React, { useState } from 'react';
import API from '../api/api';

const Chatbot = () => {
  const [question, setQuestion] = useState('');
  const [chatLog, setChatLog] = useState([]);
  const [jsonResponse, setJsonResponse] = useState(null);

  const handleSend = async () => {
    if (!question.trim()) return;
    setChatLog([...chatLog, { sender: 'user', text: question }]);
    try {
      const res = await API.post('/api/your-chat-endpoint', { prompt: question });
      const responseText = res.data.message || '응답 없음';
      setChatLog((log) => [...log, { sender: 'bot', text: responseText }]);
      setJsonResponse(res.data);
    } catch (err) {
      setChatLog((log) => [...log, { sender: 'bot', text: '에러 발생' }]);
      setJsonResponse({ error: err.response?.data || 'Unknown error' });
    }
    setQuestion('');
  };

  return (
    <div className="flex h-screen">
      <div className="w-1/2 p-4 border-r overflow-y-auto">
        <h2 className="text-lg font-bold mb-2">Chatbot</h2>
        <div className="flex flex-col gap-2 mb-4">
          {chatLog.map((msg, idx) => (
            <div key={idx} className={`p-2 rounded ${msg.sender === 'user' ? 'bg-blue-100 self-end' : 'bg-gray-200 self-start'}`}>
              {msg.text}
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            className="flex-1 border p-2"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="질문을 입력하세요..."
          />
          <button onClick={handleSend} className="bg-blue-500 text-white p-2 rounded">보내기</button>
        </div>
      </div>
      <div className="w-1/2 p-4 overflow-y-auto">
        <h2 className="text-lg font-bold mb-2">실시간 JSON 결과</h2>
        <pre className="bg-black text-green-400 p-2 rounded text-xs whitespace-pre-wrap">
          {jsonResponse ? JSON.stringify(jsonResponse, null, 2) : '응답 없음'}
        </pre>
      </div>
    </div>
  );
};

export default Chatbot;
