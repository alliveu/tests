import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000', // 나중에 AWS 배포 주소로 교체
});

// JWT 인증이 필요하다면 토큰을 헤더에 추가하는 인터셉터
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default API;
