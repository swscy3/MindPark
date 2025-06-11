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
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

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
    riskWorkersData: {
      type: Object,
      default: () => ({
        heatRiskWorkers: [],
        fallRiskWorkers: []
      })
    }
  },
  data() {
    return {
      chart: null
    };
  },
  computed: {
    // 실제 위험도별 인원 계산 (SSE 데이터 기반)
    riskCounts() {
      const allRiskWorkers = [
        ...(this.riskWorkersData.heatRiskWorkers || []),
        ...(this.riskWorkersData.fallRiskWorkers || [])
      ];
      
      const dangerCount = allRiskWorkers.filter(worker => worker.risk_level === "위험").length;
      const cautionCount = allRiskWorkers.filter(worker => worker.risk_level === "주의").length;
      const normalCount = this.totalWorkers - (dangerCount + cautionCount);
      
      return {
        normal: Math.max(0, normalCount),
        caution: cautionCount,
        danger: dangerCount
      };
    },
    // 범례 아이템들
    legendItems() {
      const total = this.totalWorkers || 1; // 0으로 나누기 방지
      
      return [
        {
          label: '정상',
          count: this.riskCounts.normal,
          percent: ((this.riskCounts.normal / total) * 100).toFixed(1),
          class: 'normal'
        },
        {
          label: '주의',
          count: this.riskCounts.caution,
          percent: ((this.riskCounts.caution / total) * 100).toFixed(1),
          class: 'caution'
        },
        {
          label: '위험',
          count: this.riskCounts.danger,
          percent: ((this.riskCounts.danger / total) * 100).toFixed(1),
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
    this.$nextTick(() => {
      this.initChart();
    });
  },
  beforeUnmount() {
    this.destroyChart();
  },
  watch: {
    riskWorkersData: {
      handler() {
        this.updateChart();
      },
      deep: true
    },
    riskCounts: {
      handler() {
        this.updateChart();
      },
      deep: true
    }
  },
  methods: {
    // 차트 초기화
    initChart() {
      if (!this.$refs.chartCanvas) return;
      
      const ctx = this.$refs.chartCanvas.getContext('2d');
      
      this.chart = new Chart(ctx, {
        type: 'doughnut',
        data: this.chartData,
        options: this.chartOptions
      });
      
      console.log('차트 초기화');
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
    }
  }
}
</script>

<style src="../css/BiometricRiskChart.css"></style>