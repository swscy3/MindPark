<template>
  <div class="biometric-risk-chart">
    <h3>{{ title }}</h3>
    <div class="chart-container">
      <canvas ref="chartCanvas" :key="chartKey"></canvas>
      <div class="center-text">
        <div class="total-count">{{ totalWorkers }}</div>
        <div class="total-label">출근자 수</div>
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
import { employeeData } from '../utils/eventBus.js'
import { watch } from 'vue'

export default {
  name: 'BiometricRiskChart',
  props: {
    title: {
      type: String,
      default: '현재 작업자 위험도 분포'
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
      chart: null,
      attendedWorkers: [],
      chartKey: 0 // 강제 리렌더링용
    };
  },
  computed: {
    totalWorkers() {
      return this.attendedWorkers.length;
    },
    riskCounts() {
      const allRiskWorkers = [
        ...(this.riskWorkersData.heatRiskWorkers || []),
        ...(this.riskWorkersData.fallRiskWorkers || [])
      ];
      
      const attendedEmpIds = this.attendedWorkers.map(worker => worker.emp_id);
      
      const dangerCount = allRiskWorkers.filter(worker => 
        worker.risk_level === "위험" && attendedEmpIds.includes(worker.emp_id)
      ).length;
      
      const cautionCount = allRiskWorkers.filter(worker => 
        worker.risk_level === "주의" && attendedEmpIds.includes(worker.emp_id)
      ).length;
      
      const normalCount = this.totalWorkers - (dangerCount + cautionCount);
      
      return {
        normal: Math.max(0, normalCount),
        caution: cautionCount,
        danger: dangerCount
      };
    },
    legendItems() {
      const total = this.totalWorkers || 1;
      
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
    }
  },
  async mounted() {
    console.log('BiometricRiskChart 마운트됨')
    
    this.updateAttendedWorkers()
    
    // 출근자 데이터 변경 감지
    watch(employeeData, () => {
      console.log('출근자 데이터 변경 감지')
      this.updateAttendedWorkers()
      this.recreateChart()
    }, { deep: true })
    
    // 동적 임포트로 Chart.js 로드
    await this.loadChartJS()
    await this.$nextTick()
    this.initChart()
  },
  beforeUnmount() {
    this.destroyChart();
  },
  watch: {
    riskWorkersData: {
      handler() {
        this.recreateChart()
      },
      deep: true
    }
  },
  methods: {
    // Chart.js 동적 로드
    async loadChartJS() {
      try {
        const Chart = await import('chart.js/auto')
        this.Chart = Chart.default
        console.log('Chart.js 로드 완료')
      } catch (error) {
        console.error('Chart.js 로드 실패:', error)
      }
    },
    
    updateAttendedWorkers() {
      const employees = employeeData.value || []
      this.attendedWorkers = employees.filter(emp => emp.attendance_status === '출근중')
      console.log('출근자 업데이트:', this.attendedWorkers.length)
    },
    
    initChart() {
      if (!this.Chart || !this.$refs.chartCanvas) {
        console.error('Chart.js 또는 캔버스가 준비되지 않음')
        return;
      }
      
      try {
        const ctx = this.$refs.chartCanvas.getContext('2d');
        
        // 완전히 독립적인 설정
        this.chart = new this.Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['정상', '주의', '위험'],
            datasets: [{
              data: [this.riskCounts.normal, this.riskCounts.caution, this.riskCounts.danger],
              backgroundColor: [
                'rgba(76, 175, 80, 0.8)',
                'rgba(255, 152, 0, 0.8)',
                'rgba(244, 67, 54, 0.8)'
              ],
              borderColor: [
                '#4CAF50',
                '#FF9800',
                '#F44336'
              ],
              borderWidth: 2
            }]
          },
          options: {
            responsive: false, // 완전히 끄기
            maintainAspectRatio: true,
            plugins: {
              legend: { display: false },
              tooltip: {
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
            }
          }
        });
        
        console.log('차트 초기화 완료');
      } catch (error) {
        console.error('차트 초기화 중 오류:', error);
      }
    },
    
    recreateChart() {
      this.destroyChart();
      this.chartKey++; // 강제 리렌더링
      this.$nextTick(() => {
        this.initChart();
      });
    },
    
    destroyChart() {
      if (this.chart) {
        try {
          this.chart.destroy();
          this.chart = null;
        } catch (error) {
          console.error('차트 제거 중 오류:', error);
        }
      }
    }
  }
}
</script>

<style src="../css/BiometricRiskChart.css"></style>