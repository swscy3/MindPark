<template>
  <div class="biometric-risk-chart">
    <h3>{{ title }}</h3>
    
    <div class="chart-container">
      <canvas ref="chartCanvas" width="300" height="300"></canvas>
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
import Chart from 'chart.js/auto';
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
      isChartReady: false,
      updateTimeout: null
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
      
      console.log('위험도 계산 결과:', {
        총출근자: this.totalWorkers,
        위험: dangerCount,
        주의: cautionCount,
        정상: normalCount
      });
      
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
  mounted() {
    console.log('BiometricRiskChart 마운트됨')
    this.updateAttendedWorkers()
    
    // 출근자 데이터 변경 감지
    watch(employeeData, () => {
      console.log('출근자 데이터 변경 감지')
      this.updateAttendedWorkers()
      this.scheduleChartUpdate()
    }, { deep: true })
    
    // 차트 초기화
    this.$nextTick(() => {
      this.initChart()
    })
  },
  beforeUnmount() {
    this.clearUpdateTimeout()
    this.destroyChart()
  },
  watch: {
    riskWorkersData: {
      handler() {
        console.log('위험자 데이터 변경됨')
        this.scheduleChartUpdate()
      },
      deep: true
    }
  },
  methods: {
    updateAttendedWorkers() {
      const employees = employeeData.value || []
      this.attendedWorkers = employees.filter(emp => emp.attendance_status === '출근중')
      console.log('출근자 업데이트:', this.attendedWorkers.length)
    },
    
    initChart() {
      if (!this.$refs.chartCanvas) {
        console.error('캔버스를 찾을 수 없습니다.')
        return;
      }
      
      // 기존 차트 정리
      this.destroyChart()
      
      try {
        const ctx = this.$refs.chartCanvas.getContext('2d');
        
        this.chart = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['정상', '주의', '위험'],
            datasets: [{
              data: [this.riskCounts.normal, this.riskCounts.caution, this.riskCounts.danger],
              backgroundColor: [
                'rgba(76, 175, 80, 0.8)',   // 정상 - 초록
                'rgba(255, 152, 0, 0.8)',   // 주의 - 주황
                'rgba(244, 67, 54, 0.8)'    // 위험 - 빨강
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
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#ffffff',
                bodyColor: '#ffffff',
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
            cutout: '60%'
          }
        });
        
        this.isChartReady = true
        console.log('차트 초기화 완료');
      } catch (error) {
        console.error('차트 초기화 실패:', error);
        this.isChartReady = false
      }
    },
    
    scheduleChartUpdate() {
      // 기존 타임아웃 클리어
      this.clearUpdateTimeout()
      
      // 100ms 후에 업데이트 실행 (빠른 연속 업데이트 방지)
      this.updateTimeout = setTimeout(() => {
        this.safeUpdateChart()
      }, 100)
    },
    
    safeUpdateChart() {
      if (!this.isChartReady || !this.chart) {
        console.log('차트가 준비되지 않아 업데이트 생략')
        return
      }
      
      try {
        // 차트 인스턴스 유효성 검사
        if (!this.chart.canvas || !this.chart.canvas.parentNode) {
          console.log('차트 캔버스가 DOM에서 제거됨, 재초기화 필요')
          this.reinitializeChart()
          return
        }
        
        // 데이터 업데이트
        const newData = [
          this.riskCounts.normal, 
          this.riskCounts.caution, 
          this.riskCounts.danger
        ]
        
        this.chart.data.datasets[0].data = newData
        this.chart.update('active') // 'none' 대신 'active' 사용
        
        console.log('차트 데이터 업데이트 완료:', newData)
      } catch (error) {
        console.error('차트 업데이트 실패:', error)
        // 업데이트 실패 시 재초기화
        this.reinitializeChart()
      }
    },
    
    reinitializeChart() {
      console.log('차트 재초기화 시작')
      this.isChartReady = false
      
      this.$nextTick(() => {
        this.initChart()
      })
    },
    
    clearUpdateTimeout() {
      if (this.updateTimeout) {
        clearTimeout(this.updateTimeout)
        this.updateTimeout = null
      }
    },
    
    destroyChart() {
      if (this.chart) {
        try {
          this.chart.destroy()
          console.log('차트 제거 완료')
        } catch (error) {
          console.error('차트 제거 실패:', error)
        }
        this.chart = null
      }
      this.isChartReady = false
    }
  }
}
</script>

<style src="../css/BiometricRiskChart.css"></style>