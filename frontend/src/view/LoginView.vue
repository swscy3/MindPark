<template>
  <div class="login-container">
    <h1 class="login-title">야외 근로자 건강 상태 모니터링 시스템</h1>
    <form class="login-form" @submit.prevent="login">
      <div class="input-group">
        <input
          type="text"
          placeholder="사번 입력"
          v-model="id"
        />
      </div>
      <div class="input-group">
        <input
          type="password"
          placeholder="생년월일 입력 (YYYYMMDD)"
          v-model="password"
        />
      </div>
      <button class="login-button" type="submit">
        로그인
      </button>
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LoginView',
  data() {
    return {
      id: "",
      password: "",
      errorMessage: "",
    };
  },
  methods: {
    async login() {
      // 입력값 검증
      if (!this.id || !this.password) {
        this.errorMessage = "사번과 생년월일을 모두 입력하세요.";
        return;
      }
      
      try {
        this.errorMessage = "";
        console.log('로그인 시도:', this.id);
        
        // 백엔드 서버에 인증 요청
        const response = await axios.post('http://orion.mokpo.ac.kr:8485/api/web/auth/login', {
          id: this.id,
          password: this.password
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        console.log('로그인 응답:', response.data);
        
        // 백엔드에서 받은 토큰 확인 및 저장
        if (response.data && response.data.token) {
          console.log('토큰 수신 성공');
          // 토큰 저장
          localStorage.setItem('token', response.data.token);
          
          // 로그인 성공 후 메인 페이지로 이동
          console.log('메인 페이지로 이동');
          this.$router.push({ name: "Main" });
        } else {
          this.errorMessage = "로그인 실패: 인증 토큰을 받지 못했습니다.";
          console.error('토큰 없음:', response.data);
        }
      } catch (error) {
        console.error('로그인 오류:', error);
        
        // 백엔드에서 오류 응답이 온 경우
        if (error.response) {
          console.log('오류 응답 상태:', error.response.status);
          console.log('오류 응답 데이터:', error.response.data);
          
          if (error.response.status === 401) {
            this.errorMessage = "사번 또는 생년월일이 올바르지 않습니다.";
          } else if (error.response.data && error.response.data.message) {
            this.errorMessage = error.response.data.message;
          } else {
            this.errorMessage = "로그인 처리 중 오류가 발생했습니다.";
          }
        } else if (error.request) {
          // 서버에 요청은 갔지만 응답이 없는 경우
          this.errorMessage = "서버에 연결할 수 없습니다. 네트워크를 확인하세요.";
          console.error('응답 없음:', error.request);
        } else {
          // 요청 설정 중 오류 발생
          this.errorMessage = "로그인 요청 중 오류가 발생했습니다.";
          console.error('요청 오류:', error.message);
        }
      }
    }
  },
  // 컴포넌트 마운트 시 이미 인증되어 있는지 확인
  mounted() {
    const token = localStorage.getItem('token');
    console.log('로그인 화면 마운트, 토큰 존재 여부:', !!token);
    if (token) {
      console.log('토큰 있음, 메인 페이지로 이동');
      this.$router.push({ name: 'Main' });
    }
  }
};
</script>

<style src="../css/Login.css"></style>