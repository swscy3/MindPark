<template>
 <div class="top-bar">
   <!-- 오류 메시지 표시 영역 -->
   <div v-if="showErrorMessage" class="error-message">
     {{ error }}
   </div>
   
   <!-- 관리자 정보 섹션 -->
   <div class="top-bar__section admin-section">
     <p>안녕하세요 {{ headerData.man_name }}님<br/>현장명: 청계 건설현장</p>
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
       <p v-else>내일 09시 전체 조회 진행 예정입니다.</p>
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
       man_name: '관리자',
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
       const response = await axios.get('http://orion.mokpo.ac.kr:8495/api/util/weather', {
         headers: {
           'Authorization': `Bearer ${token}`,
           'Accept': 'application/json'
         }
       });
       
       console.log('API 응답:', response.data);
       console.log('응답 타입:', typeof response.data);
       
       // HTML 응답인지 확인
       if (typeof response.data === 'string' && response.data.includes('<!doctype html>')) {
         throw new Error('서버에서 HTML 페이지를 반환했습니다. API 엔드포인트를 확인해주세요.');
       }
       
       // API 응답 데이터를 내부 구조에 맞게 변환
       if (response.data && typeof response.data === 'object') {
         // 날씨 데이터 매핑
         this.headerData.site_temp = response.data.temperature ? 
           parseFloat(response.data.temperature.replace('°C', '')) : 0;
         this.headerData.site_humi = response.data.humidity ? 
           parseFloat(response.data.humidity.replace('%', '')) : 0;
         this.headerData.site_wind = response.data.windSpeed ? 
           parseFloat(response.data.windSpeed.replace('m/s', '')) : 0;
         
         // 사용자 정보가 localStorage에 있다면 가져오기
         const userInfo = localStorage.getItem('userInfo');
         if (userInfo) {
           try {
             const parsedUserInfo = JSON.parse(userInfo);
             // admin 객체 구조에 맞게 수정
             this.headerData.man_name = parsedUserInfo.admin?.name || parsedUserInfo.name || '관리자';
             
             // 사진 경로를 웹 접근 가능한 URL로 변환
             const picturePath = parsedUserInfo.admin?.picture || parsedUserInfo.picture;
             if (picturePath) {
               try {
                 // Docker 내부에서 정적 파일 접근 시도
                 this.headerData.man_photo = `http://orion.mokpo.ac.kr:8495${picturePath}`;
                 
                 console.log('변환된 사진 URL:', this.headerData.man_photo);
               } catch (imgError) {
                 console.error('이미지 처리 오류:', imgError);
                 this.headerData.man_photo = ''; // 에러 시 빈 문자열
               }
             }
             
           } catch (e) {
             console.error('사용자 정보 파싱 오류:', e);
           }
         } else {
           console.log('localStorage에 userInfo가 없습니다');
           // userInfo가 없으면 사용자 정보 API 호출
           await this.fetchUserInfo(token);
         }
         
         console.log('변환된 날씨 데이터:', {
           temp: this.headerData.site_temp,
           humi: this.headerData.site_humi,
           wind: this.headerData.site_wind
         });
       } else {
         throw new Error('올바르지 않은 API 응답 형식입니다.');
       }
       
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
   },
   
   async fetchUserInfo(token) {
     try {
       // 사용자 정보를 가져오는 별도 API가 있다면 사용
       // 예시: /api/user/profile 등
       console.log('사용자 정보를 별도로 가져와야 합니다');
       // const userResponse = await axios.get('http://orion.mokpo.ac.kr:8485/api/user/profile', {
       //   headers: { 'Authorization': `Bearer ${token}` }
       // });
       // localStorage.setItem('userInfo', JSON.stringify(userResponse.data));
     } catch (error) {
       console.error('사용자 정보 조회 실패:', error);
     }
   }
 }
}
</script>

<style src="../css/TopBar.css"></style>