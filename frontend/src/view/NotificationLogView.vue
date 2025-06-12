<template>
  <div class="notification-log-container">
    <v-card class="notification-log-card">
      <v-card-title class="notification-log-title">
        알림 로그 조회
      </v-card-title>
      
      <!-- SearchBox 컴포넌트만 사용 -->
      <div class="search-section">
        <SearchBox 
          v-model="filters.keyword"
          placeholder="사번, 이름, 증상, 조치사항 검색"
          @search="handleSearch"
        />
      </div>
      
      <NotificationTable 
        :notifications="paginatedNotifications" 
        :loading="loading"
        @edit="openEditModal"
      />
      
      <!-- 페이지네이션 추가 -->
      <div class="pagination">
        <button 
          class="pagination-button" 
          :disabled="currentPage === 1" 
          @click="currentPage--"
        >
          &lt;
        </button>
        
        <button 
          v-for="page in totalPages" 
          :key="page" 
          class="pagination-button" 
          :class="{ 'active': currentPage === page }"
          @click="currentPage = page"
        >
          {{ page }}
        </button>
        
        <button 
          class="pagination-button" 
          :disabled="currentPage === totalPages" 
          @click="currentPage++"
        >
          &gt;
        </button>
      </div>
      
      <NotificationEditModal 
        v-if="selectedNotification"
        :notification="selectedNotification"
        :show="showEditModal"
        @close="closeEditModal"
        @save="saveNotification"
      />
    </v-card>
  </div>
</template>

<script>
import axios from 'axios';
import SearchBox from '../components/SearchBox.vue';
import NotificationTable from '../components/NotificationTable.vue';
import NotificationEditModal from '../components/NotificationEditModal.vue';

export default {
  name: 'NotificationLogView',
  
  components: {
    SearchBox,
    NotificationTable,
    NotificationEditModal
  },
  
  data() {
    return {
      notifications: [],
      filteredNotifications: [],
      loading: false,
      filters: {
        keyword: ''
      },
      selectedNotification: null,
      showEditModal: false,
      
      // 페이지네이션 관련
      currentPage: 1,
      pageSize: 10,
      
      // SSE 연결 관리
      eventSource: null,
      error: null
    };
  },
  
  computed: {
    // 페이지네이션을 위한 계산된 속성
    totalPages() {
      return Math.ceil(this.filteredNotifications.length / this.pageSize);
    },
    
    // 현재 페이지에 표시할 알림 데이터
    paginatedNotifications() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredNotifications.slice(start, end);
    }
  },
  
  watch: {
    // 키워드 변경 시 자동으로 필터 적용
    'filters.keyword'() {
      this.applyFilters();
      this.currentPage = 1; // 검색 시 첫 페이지로 이동
    }
  },
  
  methods: {
    // API 응답 데이터를 컴포넌트 형식으로 변환
    mapApiToComponent(apiData) {
      return {
        id: apiData.anomaly_id,
        employeeId: apiData.emp_id,
        name: apiData.emp_name,
        symptom: apiData.symptom,
        treatment: apiData.management ? apiData.management.action_content || '' : apiData.action_content || '',
        createdAt: apiData.anomaly_time,
        updatedAt: apiData.management ? apiData.management.updated_at : apiData.updated_at,
        editStatus: apiData.status,
        risk: apiData.management ? apiData.management.risk : apiData.risk,
        isNew: this.isRecentNotification(apiData.anomaly_time)
      };
    },
    
    // 최근 알림인지 확인 (2시간 이내를 새 알림으로 처리)
    isRecentNotification(anomalyTime) {
      const now = new Date();
      const alertTime = new Date(anomalyTime);
      const diffHours = (now - alertTime) / (1000 * 60 * 60);
      return diffHours <= 2;
    },
    
    async fetchNotifications() {
      this.loading = true;
      
      // 기존 SSE 연결이 있으면 종료
      this.stopSSEConnection();
      
      try {
        // 새로운 토큰 사용
       const token = localStorage.getItem('token');

        console.log('SSE 연결 시작...');
        
        // SSE URL에 토큰을 쿼리 파라미터로 추가
        const sseUrl = `http://orion.mokpo.ac.kr:8485/api/web/alert/anomalies/stream?token=${token}`;
        
        // EventSource 생성
        this.eventSource = new EventSource(sseUrl);
        
        // 연결 성공
        this.eventSource.onopen = (event) => {
          console.log('SSE 연결 성공');
          this.loading = false;
          this.error = null;
        };
        
        // 메시지 수신
        this.eventSource.onmessage = (event) => {
          try {
            console.log('SSE 원본 데이터:', event.data);
            const responseData = JSON.parse(event.data);
            console.log('SSE 파싱된 데이터:', responseData);
            
            if (responseData.status === 'success' && responseData.data) {
              // API 응답이 배열인지 단일 객체인지 확인
              const apiData = Array.isArray(responseData.data) 
                ? responseData.data 
                : [responseData.data];
              
              // API 데이터를 컴포넌트 형식으로 매핑
              this.notifications = apiData.map(item => this.mapApiToComponent(item));
              
              // 정렬: 완료된 것은 아래로, 나머지는 최신순
              this.notifications.sort((a, b) => {
                // 완료 상태 우선 처리
                if (a.editStatus === '완료' && b.editStatus !== '완료') return 1;
                if (a.editStatus !== '완료' && b.editStatus === '완료') return -1;
                
                // 같은 상태면 최신순
                return new Date(b.createdAt) - new Date(a.createdAt);
              });
              
              this.filteredNotifications = [...this.notifications];
              console.log('알림 데이터 업데이트 완료:', this.notifications);
              this.loading = false;
              this.error = null;
            } else if (responseData.status === 'error') {
              console.error('SSE 에러 응답:', responseData.message);
              this.handleApiError(responseData.message || '서버에서 오류가 발생했습니다.');
              this.loading = false;
            } else if (responseData.status === 'connected') {
              console.log('SSE 연결 확인:', responseData.message);
              this.loading = false;
            }
          } catch (parseError) {
            console.error('SSE 데이터 파싱 오류:', parseError, event.data);
          }
        };
        
        // 연결 오류 처리
        this.eventSource.onerror = (event) => {
          console.error('SSE 연결 오류:', event);
          this.loading = false;
          
          if (this.eventSource.readyState === EventSource.CLOSED) {
            console.log('SSE 연결이 종료됨');
            this.error = '서버 연결이 종료되었습니다.';
          } else if (this.eventSource.readyState === EventSource.CONNECTING) {
            console.log('SSE 재연결 시도 중...');
            this.error = '서버에 연결 중입니다...';
          }
        };
        
      } catch (error) {
        console.error('SSE 초기화 오류:', error);
        this.loading = false;
        this.error = '연결 초기화 중 오류가 발생했습니다.';
      }
    },
    
    // SSE 연결 종료
    stopSSEConnection() {
      if (this.eventSource) {
        console.log('SSE 연결 종료');
        this.eventSource.close();
        this.eventSource = null;
      }
    },
    
    async saveNotificationToApi(updatedNotification) {
      try {
        // 새로운 토큰 사용
        const token = localStorage.getItem('token');

        // 디버깅용 로그
        console.log('=== 저장 요청 데이터 ===');
        console.log('anomaly_id:', updatedNotification.id);
        console.log('editStatus:', updatedNotification.editStatus);
        console.log('treatment:', updatedNotification.treatment);

        const requestBody = {
          anomaly_id: updatedNotification.id,
          status: updatedNotification.editStatus === '처리 완료' ? '완료' : '처리중',
          action_content: updatedNotification.treatment || ''
        };

        console.log('=== 실제 전송할 Body ===');
        console.log(requestBody);

        // 업데이트 API 호출 (Bearer Token 방식)
        const response = await axios.post(
          `http://orion.mokpo.ac.kr:8485/api/web/alert/anomalies/update`,
          requestBody,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        if (response.data.status === 'success') {
          // 서버가 반환하는 전체 목록으로 notifications 업데이트
          if (response.data.data && response.data.data.all_anomalies) {
            const apiData = response.data.data.all_anomalies;
            this.notifications = apiData.map(item => this.mapApiToComponent(item));
            
            // 정렬: 완료된 것은 아래로, 나머지는 최신순
            this.notifications.sort((a, b) => {
              // 완료 상태 우선 처리
              if (a.editStatus === '완료' && b.editStatus !== '완료') return 1;
              if (a.editStatus !== '완료' && b.editStatus === '완료') return -1;
              
              // 같은 상태면 최신순
              return new Date(b.createdAt) - new Date(a.createdAt);
            });
            
            this.applyFilters(); // 필터 재적용
          }
          return true;
        } else {
          console.error('Save API Error:', response.data.message);
          return false;
        }
      } catch (error) {
        console.error('Failed to save notification:', error);
        return false;
      }
    },
    
    handleApiError(message) {
      // API 에러 처리
      this.$toast?.error(`API 오류: ${message}`);
    },
    
    handleNetworkError(error) {
      // 네트워크 오류 처리
      this.$toast?.error('네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    },
    
    // SearchBox에서 검색 이벤트 처리
    handleSearch(keyword) {
      // 실시간 검색이므로 추가 동작 불필요
      // watch에서 자동으로 applyFilters 호출됨
    },
    
    applyFilters() {
      let result = [...this.notifications];
      
      // 키워드 필터
      if (this.filters.keyword) {
        const keyword = this.filters.keyword.toLowerCase();
        result = result.filter(item => 
          item.employeeId.toLowerCase().includes(keyword) ||
          item.name.toLowerCase().includes(keyword) ||
          item.symptom.toLowerCase().includes(keyword) || 
          item.treatment.toLowerCase().includes(keyword)
        );
      }
      
      this.filteredNotifications = result;
    },
    
    async openEditModal(notification) {
      try {
        // 새로운 토큰 사용
        const token = localStorage.getItem('token');

        // Bearer Token 방식으로 상세 정보 조회 (쿼리 파라미터 방식 사용)
        const response = await axios.get(
          `http://orion.mokpo.ac.kr:8485/api/web/alert/anomalies/detail?anomaly_id=${notification.id}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );

        if (response.data.status === 'success') {
          // API에서 받은 최신 데이터로 모달 표시
          this.selectedNotification = this.mapApiToComponent(response.data.data);
          this.showEditModal = true;
        } else {
          console.error('Detail API Error:', response.data.message);
          // API 실패 시 기존 데이터로 모달 표시
          this.selectedNotification = { ...notification };
          this.showEditModal = true;
        }
      } catch (error) {
        console.error('Failed to fetch notification detail:', error);
        // 에러 시 기존 데이터로 모달 표시
        this.selectedNotification = { ...notification };
        this.showEditModal = true;
      }
    },
    
    closeEditModal() {
      this.showEditModal = false;
      this.selectedNotification = null;
    },
    
    async saveNotification(updatedNotification) {
      // API로 저장
      const success = await this.saveNotificationToApi(updatedNotification);
      
      if (success) {
        // saveNotificationToApi에서 이미 전체 데이터를 업데이트했으므로
        // 여기서는 추가 로컬 업데이트 불필요
        this.$toast?.success('알림이 성공적으로 저장되었습니다.');
        this.closeEditModal();
      } else {
        this.$toast?.error('저장 중 오류가 발생했습니다.');
      }
    }
  },
  
  created() {
    this.fetchNotifications();
  },
  
  beforeUnmount() {
    // 컴포넌트 언마운트 시 SSE 연결 정리
    this.stopSSEConnection();
  }
};
</script>

<style src="../css/NotificationLog.css"></style>