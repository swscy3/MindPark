import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../view/LoginView.vue'
import MainView from '../view/MainView.vue'
import WorkerStatusView from '../view/WorkerStatusView.vue'
import WorkerSearchView from '../view/WorkerSearchView.vue'
import NotificationLogView from '../view/NotificationLogView.vue'
import ResponseManualView from '../view/ResponseManualView.vue'

const routes = [
  // 로그인 라우트
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  
  // 메인 라우트
  {
    path: '/',
    name: 'Main',
    component: MainView
  },
  
  // 작업자 현황 라우트
  {
    path: '/workerstatus',
    name: 'WorkerStatus',
    component: WorkerStatusView
  },

  // 작업자 조회 라우트
  {
    path: '/workersearch',
    name: 'WorkerSearch',
    component: WorkerSearchView
  },

  // 알림 로그
  {
    path: '/notificationlog',
    name: 'NotificationLog',
    component: NotificationLogView
  },

  // 위험 대응 매뉴얼 라우트
  {
    path: '/responsemanual',
    name: 'ResponseManual',
    component: ResponseManualView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 네비게이션 가드 수정 - 더 명확한 로깅 추가
router.beforeEach((to, from, next) => {
  console.log('현재 경로:', to.path);
  console.log('이동 전 경로:', from.path);
  
  // 로그인 상태 확인 (토큰 존재 여부)
  const token = localStorage.getItem('token');
  console.log('토큰 존재 여부:', !!token);
  
  // 로그인 페이지로 가는 경우는 항상 허용
  if (to.path === '/login') {
    console.log('로그인 페이지로 이동 허용');
    next();
    return;
  }
  
  // 인증되지 않은 상태에서 로그인 페이지가 아닌 다른 페이지로 접근하려고 할 때
  if (!token) {
    console.log('인증되지 않음, 로그인 페이지로 리다이렉트');
    next('/login');
  } else {
    console.log('인증됨, 요청한 페이지로 이동');
    next();
  }
});

export default router