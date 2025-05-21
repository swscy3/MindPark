<template>
  <div class="top-bar">
    <!-- 오류 메시지 표시 영역 -->
    <div v-if="showErrorMessage" class="error-message">
      {{ error }}
    </div>
    
    <!-- 관리자 정보 섹션 -->
    <div class="top-bar__section admin-section">
      <p>안녕하세요 {{ headerData.man_name }}님<br/>현장명: 서울 강남 건설현장</p>
      <!-- 관리자 프로필 사진 (없으면 기본 아이콘 표시) -->
      <div class="admin-photo">
        <v-avatar size="40">
          <v-img v-if="headerData.man_photo" :src="headerData.man_photo" alt="관리자 사진"></v-img>
          <v-icon v-else>mdi-account</v-icon>
        </v-avatar>
      </div>
    </div>
    
    <!-- 날씨 정보 섹션 -->
    <div class="top-bar__section weather-section">
      <p>현장 날씨 정보</p>
      <div class="weather-info">
        <!-- 날씨 데이터가 로딩된 경우 -->
        <div v-if="!loading">
          <p><strong>온도: </strong> {{ headerData.site_temp }}°C</p>
          <p><strong>습도: </strong> {{ headerData.site_humi }}%</p>
          <p><strong>풍속: </strong> {{ headerData.site_wind }}m/s</p>
        </div>
        <!-- 날씨 데이터 로딩 중인 경우 -->
        <p v-else>날씨 정보를 불러오는 중...</p>
      </div>
    </div>
    
    <!-- 공지사항 섹션 -->
    <div class="top-bar__section notices-section">
      <p>공지사항 및 알림</p>
      <div class="notices-list">
        <!-- 공지사항이 있는 경우 -->
        <div v-if="headerData.notice_title && headerData.notice_title.length > 0">
          <!-- 공지사항 목록 (최대 maxNotices개) -->
          <div v-for="(notice, index) in displayedNotices" :key="index" class="notice-item">
            {{ notice }}
          </div>
          <!-- 추가 공지사항이 있는 경우 "더보기" 표시 -->
          <div 
            v-if="headerData.notice_title.length > maxNotices" 
            class="more-notices" 
            @click="$emit('show-all-notices')"
          >
            외 {{ headerData.notice_title.length - maxNotices }}건 더보기
          </div>
        </div>
        <!-- 공지사항이 없는 경우 기본 메시지 표시 -->
        <p v-else>폭염주의보 발령: 충분한 수분 섭취 바랍니다.</p>
        <p>내일 09시 전체 조회 진행 예정입니다.</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import router from '../router'; // 라우터 임포트 추가

export default {
  name: 'TopBar',
  data() {
    return {
      headerData: {
        man_name: '',
        man_photo: '',
        site_temp: 0,
        site_humi: 0,
        site_wind: 0,
        notice_title: []
      },
      maxNotices: 3,
      loading: true,
      error: null,
      showErrorMessage: false
    };
  },
  computed: {
    displayedNotices() {
      return this.headerData.notice_title 
        ? this.headerData.notice_title.slice(0, this.maxNotices)
        : [];
    }
  },
  mounted() {
    this.fetchHeaderData();
  },
  methods: {
    async fetchHeaderData() {
      this.loading = true;
      this.error = null;
      this.showErrorMessage = false;
      
      try {
        // localStorage에서 토큰 가져오기 (jwt_token에서 token으로 변경)
        const token = localStorage.getItem('token');
        console.log('토큰 존재 여부:', !!token);
        
        // 토큰이 없으면 로그인 페이지로 리다이렉트
        if (!token) {
          console.log('토큰 없음, 로그인 페이지로 리다이렉트');
          router.push('/login');
          return;
        }
        
        // API 호출
        const response = await axios.get('http://orion.mokpo.ac.kr:8485/api/web/header', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          }
        });
        
        console.log('API 응답:', response.data);
        
        // API 응답 데이터를 상태에 저장
        this.headerData = response.data;
        
        // notice_title이 없는 경우 빈 배열로 초기화
        if (!this.headerData.notice_title) {
          this.headerData.notice_title = [];
        }
      } catch (err) {
        console.error('API 호출 중 오류:', err);
        
        if (err.response) {
          const status = err.response.status;
          console.log('오류 응답 상태:', status);
          console.log('오류 응답 데이터:', err.response.data);
          
          // 인증 오류인 경우 로그인 페이지로 리다이렉트
          if (status === 401 || status === 403) {
            this.error = '인증에 실패했습니다. 다시 로그인해주세요.';
            console.log('인증 오류, 로그인 페이지로 리다이렉트');
            localStorage.removeItem('token'); // 토큰 제거
            router.push('/login');
          } else if (status === 404) {
            this.error = '사용자 정보를 찾을 수 없습니다';
          } else if (status === 500) {
            this.error = '서버 오류가 발생했습니다';
          } else {
            this.error = `API 오류: HTTP ${status}`;
          }
        } else if (err.request) {
          this.error = '서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.';
        } else {
          this.error = `요청 오류: ${err.message}`;
        }
        
        this.showErrorMessage = true;
        console.error('API 오류:', this.error);
      } 
      finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style src="../css/TopBar.css"></style>