import React, { useState } from 'react';
import API from '../api/api';

const LoginPage = () => {
  const [form, setForm] = useState({ email: '', password: '' });
  const [message, setMessage] = useState('');

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post('/api/auth/login', form);
      localStorage.setItem('token', res.data.token); // 토큰 저장
      setMessage('로그인 성공');
    } catch (err) {
      setMessage(err.response?.data?.message || '에러 발생');
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <h1 className="text-xl font-bold mb-4">로그인</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-2">
        <input name="email" placeholder="Email" value={form.email} onChange={handleChange} className="border p-2"/>
        <input name="password" type="password" placeholder="Password" value={form.password} onChange={handleChange} className="border p-2"/>
        <button type="submit" className="bg-green-500 text-white p-2 rounded">로그인</button>
      </form>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
};

export default LoginPage;
