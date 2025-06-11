<template>
  <div class="main-content">
    <!-- 상단 바 -->
    <TopBar @show-all-notices="showAllNotices"/>

    <!-- 페이지 내용 - 홈 화면이 아닌 경우 라우터 뷰 사용 -->
    <router-view v-if="$route.name !== 'Main'"></router-view>
    
    <!-- 홈 화면 콘텐츠 -->
    <Dashboard 
      v-else
      v-if="!loading"
      :risk-workers-data="riskWorkersData"
      :statistics-data="statisticsData"
      @show-worker-detail="showWorkerDetail"
      @navigate="navigateTo"
      @refresh-data="fetchDashboardData"
    />

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>데이터를 불러오는 중...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-if="error && !loading" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button @click="manualReconnect" class="retry-button">다시 연결</button>
    </div>
  </div>
</template>

<script>
import TopBar from '../components/TopBar.vue';
import Dashboard from '../components/DashBoard.vue';
import axios from 'axios';

export default {
  name: 'MainView',
  components: {
    TopBar,
    Dashboard
  },
  data() {
    return {
      // API 데이터 상태
      dashboardData: null,
      loading: false,
      error: null,
      
      // SSE 연결 상태
      eventSource: null,
      
      // 재연결 관리
      reconnectAttempts: 0,
      maxReconnectAttempts: 5,
      reconnectDelay: 2000, // 2초
      
      // 선택된 작업자 정보
      selectedWorker: null
    };
  },
  computed: {
    // 대시보드에 전달할 위험 작업자 데이터
    riskWorkersData() {
      if (!this.dashboardData) {
        return {
          heatRiskWorkers: [],
          fallRiskWorkers: [],
          sosCount: 0
        };
      }
      
      return {
        heatRiskWorkers: this.dashboardData.heat_risk_employees || [],
        fallRiskWorkers: this.dashboardData.fall_risk_employees || [],
        sosCount: this.calculateSosCount()
      };
    },
    
    // 대시보드에 전달할 통계 데이터
    statisticsData() {
      if (!this.dashboardData) {
        return {
          workerStats: {
            planned: 0,
            present: 0,
            absent: 0
          },
          riskStats: {
            gradeA: 0,
            gradeB: 0,
            gradeC: 0
          },
          deviceStats: {
            total: 0,
            active: 0,
            inactive: 0,
            error: 0,
            smartWatch: 0,
            bioSensor: 0,
            envSensor: 0
          }
        };
      }
      
      const deviceStatus = this.dashboardData.device_status || {};
      
      return {
        workerStats: this.calculateWorkerStats(),
        riskStats: this.calculateRiskStats(),
        deviceStats: {
          total: deviceStatus.total_devices || 0,
          active: deviceStatus.active_devices || 0,
          inactive: deviceStatus.inactive_devices || 0,
          error: 0, // API에서 제공되지 않는 경우 기본값
          smartWatch: 0, // API에서 제공되지 않는 경우 기본값
          bioSensor: 0, // API에서 제공되지 않는 경우 기본값
          envSensor: 0, // API에서 제공되지 않는 경우 기본값
          lastUpdated: deviceStatus.last_updated
        }
      };
    }
  },
  async mounted() {
    // 토큰 확인
    const token = localStorage.getItem('token');
    if (!token) {
      console.log('토큰 없음, 로그인 페이지로 이동');
      this.$router.push({ name: 'Login' });
      return;
    }
    
    // SSE 연결 시작
    this.fetchDashboardData();
  },
  beforeUnmount() {
    // 컴포넌트 언마운트 시 SSE 연결 정리
    this.stopSSEConnection();
  },
  methods: {
    // SSE 연결 시작
    async fetchDashboardData() {
      // 기존 연결이 있으면 종료
      this.stopSSEConnection();
      
      this.loading = true;
      this.error = null;
      
      try {
        // JWT 토큰 가져오기
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('인증 토큰이 없습니다');
        }
        
        console.log('SSE 연결 시작...');
        
        // SSE URL에 토큰을 쿼리 파라미터로 추가
        const sseUrl = `/api/web/monitoring/dashboard/stream?token=${encodeURIComponent(token)}`;
        
        // EventSource 생성
        this.eventSource = new EventSource(sseUrl);
        
        // 연결 성공
        this.eventSource.onopen = (event) => {
          console.log('SSE 연결 성공');
          this.loading = false;
          this.error = null;
          this.reconnectAttempts = 0; // 재연결 시도 횟수 리셋
        };
        
        // 메시지 수신
        this.eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('SSE 데이터 수신:', data);
            
            if (data.status === 'success' && data.data) {
              this.dashboardData = data.data;
              console.log('대시보드 데이터 업데이트 완료');
              this.loading = false;
              this.error = null;
            } else if (data.status === 'error') {
              console.error('SSE 에러 응답:', data.message);
              this.error = data.message || '서버에서 오류가 발생했습니다.';
              this.loading = false;
            } else if (data.status === 'connected') {
              console.log('SSE 연결 확인:', data.message);
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
            
            // 자동 재연결 시도
            this.attemptReconnect();
          } else if (this.eventSource.readyState === EventSource.CONNECTING) {
            console.log('SSE 재연결 시도 중...');
            this.error = '서버에 연결 중입니다...';
          }
        };
        
      } catch (error) {
        console.error('SSE 초기화 오류:', error);
        this.loading = false;
        
        if (error.message.includes('인증 토큰')) {
          this.error = '로그인이 필요합니다.';
          this.$router.push({ name: 'Login' });
        } else {
          this.error = '연결 초기화 중 오류가 발생했습니다.';
        }
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
    
    // 자동 재연결 시도
    attemptReconnect() {
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.log('최대 재연결 시도 횟수 초과');
        this.error = '서버에 연결할 수 없습니다. 페이지를 새로고침해주세요.';
        return;
      }
      
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * this.reconnectAttempts;
      
      console.log(`${delay}ms 후 재연결 시도... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.error = `${delay / 1000}초 후 재연결 시도 중... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`;
      
      setTimeout(() => {
        this.fetchDashboardData();
      }, delay);
    },
    
    // 수동 재연결
    manualReconnect() {
      this.reconnectAttempts = 0;
      this.fetchDashboardData();
    },
    
    // SOS 카운트 계산 (위험 수준이 '위험'인 작업자 수)
    calculateSosCount() {
      const heatRiskCount = (this.dashboardData.heat_risk_employees || [])
        .filter(worker => worker.risk_level === '위험').length;
      const fallRiskCount = (this.dashboardData.fall_risk_employees || [])
        .filter(worker => worker.risk_level === '위험').length;
      
      return heatRiskCount + fallRiskCount;
    },
    
    // 작업자 통계 계산
    calculateWorkerStats() {
      const totalHeat = (this.dashboardData.heat_risk_employees || []).length;
      const totalFall = (this.dashboardData.fall_risk_employees || []).length;
      const totalPresent = totalHeat + totalFall;
      
      // 실제 계획 인원은 별도 API에서 가져와야 할 수도 있음
      const planned = this.dashboardData.device_status?.total_devices || totalPresent;
      
      return {
        planned: planned,
        present: totalPresent,
        absent: Math.max(0, planned - totalPresent)
      };
    },
    
    // 위험도 통계 계산
    calculateRiskStats() {
      const allWorkers = [
        ...(this.dashboardData.heat_risk_employees || []),
        ...(this.dashboardData.fall_risk_employees || [])
      ];
      
      const gradeA = allWorkers.filter(w => w.risk_level === '정상').length;
      const gradeB = allWorkers.filter(w => w.risk_level === '주의').length;
      const gradeC = allWorkers.filter(w => w.risk_level === '위험').length;
      
      return { gradeA, gradeB, gradeC };
    },
    
    // 페이지 이동
    navigateTo(route) {
      console.log(`Navigating to ${route}`);
      this.$router.push(`/${route}`);
    },

    // 작업자 상세 정보 표시
    showWorkerDetail(workerId) {
      console.log(`작업자 상세 정보 요청: ${workerId}`);
      
      // 온열질환 위험자에서 찾기
      let worker = (this.dashboardData?.heat_risk_employees || [])
        .find(w => w.emp_id === workerId);
      
      // 낙상 위험자에서 찾기
      if (!worker) {
        worker = (this.dashboardData?.fall_risk_employees || [])
          .find(w => w.emp_id === workerId);
      }
      
      if (worker) {
        this.selectedWorker = worker;
        // WorkerDetailModal이 구현되면 활성화:
        // this.workerDetailDialog = true;
      }
    },

    // 모든 공지사항 보기
    showAllNotices() {
      this.$router.push('/notices');
    },

    // 작업자에게 알림 전송
    async sendAlert(workerId) {
      try {
        // 실제 API 호출 구현 필요
        const response = await axios.post('/api/web/monitoring/alert', {
          emp_id: workerId,
          type: 'alert'
        });
        
        if (response.data.status === 'success') {
          alert(`${workerId} 작업자에게 알림이 전송되었습니다.`);
        }
      } catch (error) {
        console.error('알림 전송 오류:', error);
        alert('알림 전송 중 오류가 발생했습니다.');
      }
    },

    // 작업자에게 비상 연락
    async sendEmergency(workerId) {
      const confirmed = confirm(`${workerId} 작업자에게 비상 연락을 취하시겠습니까?`);
      if (confirmed) {
        try {
          // 실제 API 호출 구현 필요
          const response = await axios.post('/api/web/monitoring/emergency', {
            emp_id: workerId,
            type: 'emergency'
          });
          
          if (response.data.status === 'success') {
            alert(`${workerId} 작업자에게 비상 연락이 전송되었습니다.`);
          }
        } catch (error) {
          console.error('비상 연락 오류:', error);
          alert('비상 연락 중 오류가 발생했습니다.');
        }
      }
    }
  }
};
</script>

<style src="../css/Main.css"></style>

<style scoped>
/* 메인 콘텐츠 패딩 최적화 */
.main-content {
  padding: 20px;
}

@media (max-width: 1200px) {
  .main-content {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 12px;
  }
}
</style>