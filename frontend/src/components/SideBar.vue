<template>
  <div class="sidebar">
    <div class="logo">
      <img src="../assets/logo.png" alt="Vue 로고" />
      <h2>야외 노동자 관리 시스템</h2>
    </div>
    
    <div class="menu-item">
      <router-link to="/" class="menu-link" exact>
        <span class="icon">🏠</span>
        <span>홈</span>
      </router-link>
    </div>
    
    <div class="menu-item" :class="{ active: isWorkerMenuActive }">
      <div class="menu-header" @click="toggleWorkerMenu" :class="{ active: isCurrentRouteWorker() }">
        <span class="icon">👁️</span>
        <span>작업자 관리</span>
      </div>
      <div class="submenu" v-if="isWorkerMenuActive">
        <router-link to="/WorkerStatus" class="submenu-link">작업자 현황</router-link>
        <router-link to="/WorkerSearch" class="submenu-link">작업자 조회</router-link>
      </div>
    </div>
    
    <div class="menu-item">
      <router-link to="/notificationlog" class="menu-link">
        <span class="icon">📋</span>
        <span>알림 로그 조회</span>
      </router-link>
    </div>
    
    <div class="menu-item">
      <router-link to="/ResponseManual" class="menu-link">
        <span class="icon">📖</span>
        <span>위험 대응 매뉴얼</span>
      </router-link>
    </div>
    
    <div class="menu-item">
      <router-link to="/notices" class="menu-link">
        <span class="icon">📢</span>
        <span>공지사항</span>
      </router-link>
    </div>
    
    <!-- 로그아웃 버튼 추가 -->
    <div class="logout-container">
      <button class="logout-button" @click="logout">
        <span class="logout-icon">🚪</span>
        <span>로그아웃</span>
      </button>
    </div>
  </div>
</template>

<script>
import router from '../router';

export default {
  name: 'SideBar',
  data() {
    return {
      isWorkerMenuActive: false
    };
  },
  mounted() {
    // 현재 라우트에 따라 서브메뉴 활성화 여부 결정
    this.checkCurrentRoute();
  },
  watch: {
    '$route'() {
      this.checkCurrentRoute();
    }
  },
  methods: {
    toggleWorkerMenu() {
      this.isWorkerMenuActive = !this.isWorkerMenuActive;
    },
    checkCurrentRoute() {
      // 현재 라우트가 작업자 관련 페이지인 경우 서브메뉴 열기
      // 아닌 경우 서브메뉴 닫기
      const path = this.$route.path;
      if (path.includes('worker') || path.includes('Worker')) {
        this.isWorkerMenuActive = true;
      } else {
        this.isWorkerMenuActive = false;
      }
    },
    isCurrentRouteWorker() {
      const path = this.$route.path;
      return path.includes('worker') || path.includes('Worker');
    },
    logout() {
      localStorage.removeItem('token');
      // 로그인 페이지로 리다이렉트
      router.push('/login');
      console.log('로그아웃 성공');
    }
  }
};
</script>

<style src="../css/SideBar.css"></style>