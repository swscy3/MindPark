import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import './api/axios'
import './css/theme.css'

// 앱 초기화 함수
const initApp = () => {
  const app = createApp(App);
  app.use(router);
  app.use(vuetify)
  app.mount('#app');
  
  // 초기 인증 상태 확인
  const token = localStorage.getItem('token');
  console.log('앱 시작, 토큰 존재 여부:', !!token);
  
  // 인증되지 않은 경우 로그인 페이지로 이동
  if (!token && router.currentRoute.value.path !== '/login') {
    console.log('인증 안됨, 로그인 페이지로 이동');
    router.push('/login');
  }
};

// 앱 시작
initApp();