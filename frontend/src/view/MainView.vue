<template>
  <div class="main-content">
    <!-- 상단 바 -->
    <TopBar @show-all-notices="showAllNotices"/>

    <!-- 페이지 내용 - 홈 화면이 아닌 경우 라우터 뷰 사용 -->
    <router-view v-if="$route.name !== 'Main'"></router-view>
    
    <!-- 홈 화면 콘텐츠 -->
    <Dashboard 
      v-else
      :risk-workers-data="riskWorkersData"
      :statistics-data="statisticsData"
      @show-worker-detail="showWorkerDetail"
      @navigate="navigateTo"
    />

    <!-- 주차별 온열질환자 및 낙상자 통계 (Main 화면일 때만 표시) -->
    <div v-if="$route.name === 'Main'" class="weekly-stats-section">
      <WeeklyStats />
    </div>
  </div>
</template>

<script>
import TopBar from '../components/TopBar.vue';
import Dashboard from '../components/DashBoard.vue';
import WeeklyStats from '../components/WeeklyStats.vue';

export default {
  name: 'MainView',
  components: {
    TopBar,
    Dashboard,
    WeeklyStats
  },
  data() {
    return {
      // 위험 상태 작업자 목록 더미데이터터
      riskWorkers: [
        {
          id: 'W001',
          name: '신정우',
          temperature: 37.2,
          heartRate: 81,
          riskType: '온열질환',
          riskLevel: '위험',
          department: '토목팀',
          position: '작업반장',
          phone: '010-1234-5678'
        },
        {
          id: 'W002',
          name: '박지은',
          temperature: 36.8,
          heartRate: 88,
          riskType: '낙상',
          riskLevel: '주의',
          department: '전기팀',
          position: '기사',
          phone: '010-9876-5432',
        },
        {
          id: 'W003',
          name: '김준호',
          temperature: 37.8,
          heartRate: 92,
          riskType: '온열질환',
          riskLevel: '주의',
          department: '철근팀',
          position: '작업자',
          phone: '010-2468-1357'
        }
      ],
    };
  },
  computed: {
    // 대시보드에 전달할 위험 작업자 데이터
    riskWorkersData() {
      return {
        heatRiskWorkers: this.riskWorkers.filter(worker => worker.riskType === '온열질환'),
        fallRiskWorkers: this.riskWorkers.filter(worker => worker.riskType === '낙상'),
        sosCount: 6
      };
    },
    
    // 대시보드에 전달할 통계 데이터
    statisticsData() {
      return {
        workerStats: {
          planned: 30,
          present: 28,
          absent: 2
        },
        riskStats: {
          gradeA: 10,
          gradeB: 15,
          gradeC: 5
        },
        deviceStats: {
          total: 40,
          active: 35,
          inactive: 5
        }
      };
    }
  },
  methods: {
    // 위험도에 따른 CSS 클래스 반환
    getRiskClass(riskLevel) {
      if (riskLevel === '위험') return 'danger';
      if (riskLevel === '주의') return 'warning';
      return 'normal';
    },
    
    // 페이지 이동
    navigateTo(route) {
      console.log(`Navigating to ${route}`);
      this.$router.push(`/${route}`);
    },

    // 작업자 상세 정보 표시 (나중에 모달 구현 후 활성화)
    showWorkerDetail(workerId) {
      console.log(`작업자 상세 정보 요청: ${workerId}`);
      this.selectedWorker = this.riskWorkers.find(worker => worker.id === workerId);
      // WorkerDetailModal이 구현되면 활성화:
      // this.workerDetailDialog = true;
    },

    // 모든 공지사항 보기
    showAllNotices() {
      this.$router.push('/notices');
    },

    // 작업자에게 알림 전송
    sendAlert(workerId) {
      alert(`${workerId} 작업자에게 알림이 전송되었습니다.`);
      // 실제 API 호출 구현
    },

    // 작업자에게 비상 연락
    sendEmergency(workerId) {
      const confirmed = confirm(`${workerId} 작업자에게 비상 연락을 취하시겠습니까?`);
      if (confirmed) {
        alert(`${workerId} 작업자에게 비상 연락이 전송되었습니다.`);
        // 실제 API 호출 구현
      }
    }
  }
};
</script>

<style src="../css/Main.css"></style>

<style scoped>
.weekly-stats-section {
  margin: 20px 0;
  padding: 0;
}

@media (max-width: 768px) {
  .weekly-stats-section {
    margin: 15px 0;
  }
}
</style>