import axios from 'axios';
import router from '../router'; // 라우터 임포트

// 기본 URL 설정
axios.defaults.baseURL = 'http://orion.mokpo.ac.kr:8485';
axios.defaults.timeout = 10000; // 10초 타임아웃

// 요청 인터셉터
axios.interceptors.request.use(
  config => {
    console.log('API 요청:', config.url);
    const token = localStorage.getItem('token');
    
    if (token) {
      // 인증 토큰 추가
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // 기본 헤더 설정
    config.headers['Content-Type'] = config.headers['Content-Type'] || 'application/json';
    config.headers['Accept'] = 'application/json';
    
    return config;
  },
  error => {
    console.error('요청 오류:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터
axios.interceptors.response.use(
  response => {
    console.log('API 응답 성공:', response.config.url);
    return response;
  },
  error => {
    console.error('API 응답 오류:', error);
    
    // 인증 오류 처리 (401 Unauthorized, 403 Forbidden)
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.log('인증 오류 감지, 토큰 제거 및 로그인 페이지로 이동');
      localStorage.removeItem('token');
      router.push('/login');
    }
    
    return Promise.reject(error);
  }
);

export default axios;