<template>
  <div class="dashboard">
    <!-- 메인 레이아웃: 테이블 섹션(왼쪽)과 지도 섹션(오른쪽) -->
    <div class="main-dashboard-layout">
      <!-- 왼쪽 테이블 섹션 컨테이너 -->
      <div class="tables-container">
        <!-- 온열 질환 위험 이상자 섹션 -->
        <RiskWorkersTable 
          title="온열 질환 위험 이상자"
          :workers="heatRiskWorkers"
          :sos-count="sosCount"
          show-sos
          riskType="heat"
          @show-worker-detail="$emit('show-worker-detail', $event)"
        />
        <!-- 낙상 위험 이상자 섹션 -->
        <RiskWorkersTable 
          title="낙상 위험 이상자"
          :workers="fallRiskWorkers"
          riskType="fall"
          @show-worker-detail="$emit('show-worker-detail', $event)"
        />
      </div>
      <!-- 지도 섹션 -->
      <MapSection ref="mapSection" />
    </div>
    
    <!-- 차트 섹션 - 바이오메트릭과 온열질환자/낙상자 통계 나란히 -->
    <div class="charts-section">
      <div class="chart-left">
        <BiometricRiskChart 
          title="현재 작업자 위험도 분포"
          :total-workers="80"
          :refresh-interval="10000"
        />
      </div>
      <div class="chart-right">
        <WeeklyStats />
      </div>
    </div>
    
    <!-- 디바이스 정보 섹션 -->
    <div class="device-section">
      <DeviceInfo 
        :device-stats="deviceStats"
        @navigate="$emit('navigate', $event)"
      />
    </div>
  </div>
</template>

<script>
import RiskWorkersTable from './RiskWorkersTable.vue';
import MapSection from './MapSection.vue';
import DeviceInfo from './DeviceInfo.vue';
import BiometricRiskChart from './BiometricRiskChart.vue';
import WeeklyStats from './WeeklyStats.vue';

export default {
  name: 'Dashboard',
  components: {
    RiskWorkersTable,
    MapSection,
    DeviceInfo,
    BiometricRiskChart,
    WeeklyStats
  },
  props: {
    riskWorkersData: {
      type: Object,
      default: () => ({
        heatRiskWorkers: [],
        fallRiskWorkers: [],
        sosCount: 0
      })
    },
    statisticsData: {
      type: Object,
      default: () => ({
        workerStats: { planned: 0, present: 0, absent: 0 },
        riskStats: { gradeA: 0, gradeB: 0, gradeC: 0 },
        deviceStats: { 
          total: 0, 
          active: 0, 
          inactive: 0, 
          error: 0,
          smartWatch: 0,
          bioSensor: 0,
          envSensor: 0
        }
      })
    }
  },
  computed: {
    heatRiskWorkers() {
      return this.riskWorkersData.heatRiskWorkers || [];
    },
    fallRiskWorkers() {
      return this.riskWorkersData.fallRiskWorkers || [];
    },
    sosCount() {
      return this.riskWorkersData.sosCount || 0;
    },
    workerStats() {
      return this.statisticsData.workerStats || { planned: 0, present: 0, absent: 0 };
    },
    riskStats() {
      return this.statisticsData.riskStats || { gradeA: 0, gradeB: 0, gradeC: 0 };
    },
    deviceStats() {
      return this.statisticsData.deviceStats || {};
    }
  },
  mounted() {
    this.$nextTick(() => {
      try {
        this.initCharts();
        this.loadMap();
      } catch (e) {
        console.error('초기화 중 오류 발생:', e);
      }
    });
  },
  methods: {
    initCharts() {
      // 차트 초기화 로직
      console.log('차트 초기화');
    },
    loadMap() {
      if (this.$refs.mapSection && this.$refs.mapSection.refreshData) {
        try {
          this.$refs.mapSection.refreshData();
        } catch (e) {
          console.error('지도 로드 중 오류:', e);
        }
      }
    }
  }
}
</script>

<style src="../css/DashBoard.css"></style>