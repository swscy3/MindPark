<template>
  <v-app>
    <div class="layout">
      <!-- 로그인/회원가입 페이지가 아닐 때만 사이드바 표시 -->
      <SideBar v-if="!isAuthRoute" />
      
      <!-- 메인 콘텐츠 -->
      <div :class="{ 'main-content': !isAuthRoute, 'full-width': isAuthRoute }" :style="mainContentStyle">
        <router-view />
      </div>
    </div>
  </v-app>
</template>

<script>
import SideBar from './components/SideBar.vue';

export default {
  name: 'App',
  components: {
    SideBar
  },
  computed: {
    isAuthRoute() {
      // 로그인/회원가입 페이지인지 확인
      return this.$route.path === '/login'
    },
  }
}
</script>


<style src="./css/App.css"></style>