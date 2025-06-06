<template>
  <div class="weekly-stats">
    <h3>주차별 온열질환자 및 낙상자 통계</h3>
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
    </div>
    <div class="chart-legend">
      <div class="legend-item">
        <div class="legend-color heat"></div>
        <span>온열질환자</span>
      </div>
      <div class="legend-item">
        <div class="legend-color fall"></div>
        <span>낙상자</span>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'WeeklyStats',
  data() {
    return {
      chart: null,
      // 더미 데이터
      weeklyData: {
        labels: ['4주 전', '3주 전', '2주 전', '1주 전', '이번주'],
        heatInjuries: [2.0, 1.0, 3.0, 4.0, 2.0], // 온열질환자
        fallInjuries: [1.0, 2.0, 1.5, 1.0, 2.0]  // 낙상자
      }
    };
  },
  computed: {
    chartData() {
      return {
        labels: this.weeklyData.labels,
        datasets: [
          {
            label: '온열질환자',
            data: this.weeklyData.heatInjuries,
            backgroundColor: 'rgba(255, 99, 132, 0.3)', // 붉은색 계열
            borderColor: 'rgba(255, 99, 132, 1)', // 붉은색 계열
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: 'rgba(255, 99, 132, 1)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 5
          },
          {
            label: '낙상자',
            data: this.weeklyData.fallInjuries,
            backgroundColor: 'rgba(54, 162, 235, 0.2)', // 파란색 유지
            borderColor: 'rgba(54, 162, 235, 1)', // 파란색 유지
            borderWidth: 2,
            borderDash: [5, 5],
            fill: true,
            tension: 0.4,
            pointBackgroundColor: 'rgba(54, 162, 235, 1)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 5
          }
        ]
      };
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false // 커스텀 범례 사용
          },
          tooltip: {
            titleFont: {
              family: "'Noto Sans KR', sans-serif",
              size: 14
            },
            bodyFont: {
              family: "'Noto Sans KR', sans-serif",
              size: 13
            },
            callbacks: {
              label: (context) => {
                return `${context.dataset.label}: ${context.parsed.y}명`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 4.5,
            ticks: {
              stepSize: 0.5,
              font: {
                family: "'Noto Sans KR', sans-serif",
                size: 11
              }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            ticks: {
              font: {
                family: "'Noto Sans KR', sans-serif",
                size: 11
              }
            },
            grid: {
              display: false
            }
          }
        },
        animation: {
          duration: 1500,
          easing: 'easeOutQuart'
        },
        interaction: {
          intersect: false,
          mode: 'index'
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
    if (this.chart) {
      this.chart.destroy();
    }
  },
  methods: {
    initChart() {
      if (!this.$refs.chartCanvas) return;
      
      const ctx = this.$refs.chartCanvas.getContext('2d');
      
      this.chart = new Chart(ctx, {
        type: 'line',
        data: this.chartData,
        options: this.chartOptions
      });
    },
    updateChart() {
      if (this.chart) {
        this.chart.data = this.chartData;
        this.chart.update();
      }
    }
  }
}
</script>

<style src="../css/WeeklyStats.css"></style>