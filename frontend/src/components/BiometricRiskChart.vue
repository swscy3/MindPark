<template>
  <div class="biometric-risk-chart">
    <h3>{{ title }}</h3>
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
      <div class="center-text">
        <div class="total-count">{{ totalWorkers }}</div>
        <div class="total-label">총 작업자</div>
      </div>
    </div>
    <div class="chart-legend">
      <div class="legend-item" v-for="(item, index) in legendItems" :key="index">
        <div class="legend-color" :class="item.class"></div>
        <span class="legend-text">{{ item.label }} ({{ item.count }}명)</span>
        <span class="legend-percent">{{ item.percent }}%</span>
      </div>
    </div>
    <!-- 에러 메시지 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';
import axios from 'axios';

export default {
  name: 'BiometricRiskChart',
  props: {
    title: {
      type: String,
      default: '현재 작업자 위험도 분포'
    },
    totalWorkers: {
      type: Number,
      default: 80
    },
    refreshInterval: {
      type: Number,
      default: 10000 // 더미데이터용 10초마다 새로고침
    }
  },
  data() {
    return {
      chart: null,
      biometricData: [], // 백엔드에서 받은 위험/주의 작업자 데이터
      error: null,
      refreshTimer: null
    };
  },
  computed: {
    // 위험도별 인원 계산
    riskCounts() {
      const dangerCount = this.biometricData.filter(worker => worker.riskLevel === "위험").length;
      const cautionCount = this.biometricData.filter(worker => worker.riskLevel === "주의").length;
      const normalCount = this.totalWorkers - (dangerCount + cautionCount);
      
      return {
        normal: Math.max(0, normalCount),
        caution: cautionCount,
        danger: dangerCount
      };
    },
    // 범례 아이템들
    legendItems() {
      return [
        {
          label: '정상',
          count: this.riskCounts.normal,
          percent: ((this.riskCounts.normal / this.totalWorkers) * 100).toFixed(1),
          class: 'normal'
        },
        {
          label: '주의',
          count: this.riskCounts.caution,
          percent: ((this.riskCounts.caution / this.totalWorkers) * 100).toFixed(1),
          class: 'caution'
        },
        {
          label: '위험',
          count: this.riskCounts.danger,
          percent: ((this.riskCounts.danger / this.totalWorkers) * 100).toFixed(1),
          class: 'danger'
        }
      ];
    },
    // Chart.js 데이터
    chartData() {
      return {
        labels: ['정상', '주의', '위험'],
        datasets: [{
          data: [this.riskCounts.normal, this.riskCounts.caution, this.riskCounts.danger],
          backgroundColor: [
            'rgba(76, 175, 80, 0.8)',   // 정상 - 반투명 초록
            'rgba(255, 152, 0, 0.8)',   // 주의 - 반투명 주황
            'rgba(244, 67, 54, 0.8)'    // 위험 - 반투명 빨강
          ],
          borderColor: [
            '#4CAF50',  // 정상 - 진한 초록
            '#FF9800',  // 주의 - 진한 주황
            '#F44336'   // 위험 - 진한 빨강
          ],
          borderWidth: 3,
          hoverOffset: 15,
          hoverBorderWidth: 4
        }]
      };
    },
    // Chart.js 옵션
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            borderColor: '#ffffff',
            borderWidth: 1,
            cornerRadius: 8,
            titleFont: {
              family: "'Noto Sans KR', sans-serif",
              size: 14,
              weight: 'bold'
            },
            bodyFont: {
              family: "'Noto Sans KR', sans-serif",
              size: 13
            },
            padding: 12,
            callbacks: {
              label: (context) => {
                const value = context.parsed;
                const percentage = this.totalWorkers > 0 
                  ? ((value / this.totalWorkers) * 100).toFixed(1)
                  : 0;
                return `${context.label}: ${value}명 (${percentage}%)`;
              }
            }
          }
        },
        cutout: '65%',
        radius: '90%',
        animation: {
          animateRotate: true,
          animateScale: true,
          duration: 1500,
          easing: 'easeOutQuart'
        },
        interaction: {
          intersect: false
        }
      };
    }
  },
  mounted() {
    this.fetchBiometricData();
    this.startAutoRefresh();
  },
  beforeUnmount() {
    this.destroyChart();
    this.stopAutoRefresh();
  },
  watch: {
    riskCounts: {
      handler() {
        this.updateChart();
      },
      deep: true
    }
  },
  methods: {
    // 백엔드에서 생체데이터 가져오기
    async fetchBiometricData() {
      this.error = null;
      
      try {
        // 더미 데이터 - 위험/주의 상태인 작업자들만
        const dummyData = [
          { name: "김철수", temperature: 38.2, heartRate: 125, riskLevel: "위험" },
          { name: "이영희", temperature: 38.5, heartRate: 135, riskLevel: "위험" },
          { name: "박민수", temperature: 37.8, heartRate: 122, riskLevel: "위험" },
          { name: "최순자", temperature: 37.6, heartRate: 115, riskLevel: "주의" },
          { name: "정다운", temperature: 37.7, heartRate: 110, riskLevel: "주의" },
          { name: "김영호", temperature: 37.5, heartRate: 108, riskLevel: "주의" },
          { name: "송미래", temperature: 37.9, heartRate: 118, riskLevel: "주의" },
          { name: "장민석", temperature: 37.6, heartRate: 112, riskLevel: "주의" }
        ];
        
        this.biometricData = dummyData;
        console.log('더미 데이터 로드 완료:', this.biometricData);
        
        // 차트 초기화 또는 업데이트
        this.$nextTick(() => {
          if (!this.chart) {
            this.initChart();
          } else {
            this.updateChart();
          }
        });
        
      } catch (err) {
        console.error('데이터 로딩 중 오류:', err);
        this.error = '데이터를 불러오는 중 오류가 발생했습니다.';
        this.biometricData = [];
      }
    },
    
    // 차트 초기화
    initChart() {
      if (!this.$refs.chartCanvas) return;
      
      const ctx = this.$refs.chartCanvas.getContext('2d');
      
      this.chart = new Chart(ctx, {
        type: 'doughnut',
        data: this.chartData,
        options: this.chartOptions
      });
    },
    
    // 차트 업데이트
    updateChart() {
      if (this.chart) {
        this.chart.data = this.chartData;
        this.chart.update('none'); // 애니메이션 없이 업데이트
      }
    },
    
    // 차트 제거
    destroyChart() {
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
    },
    
    // 자동 새로고침 시작
    startAutoRefresh() {
      if (this.refreshInterval > 0) {
        this.refreshTimer = setInterval(() => {
          this.fetchBiometricData();
        }, this.refreshInterval);
      }
    },
    
    // 자동 새로고침 중지
    stopAutoRefresh() {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer);
        this.refreshTimer = null;
      }
    },
    
    // 수동 새로고침
    refresh() {
      this.fetchBiometricData();
    }
  }
}
</script>

<style src="../css/BiometricRiskChart.css"></style>