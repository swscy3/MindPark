<!-- <template>
  <div class="statistics-graph">
    <h3>{{ title }}</h3>
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'StatisticsGraph',
  props: {
    title: {
      type: String,
      default: '통계 그래프'
    },
    labels: {
      type: Array,
      default: () => ['예정', '출근', '결근']
    },
    values: {
      type: Array,
      default: () => [30, 28, 2]
    }
  },
  data() {
    return {
      chart: null
    };
  },
  computed: {
    chartData() {
      return {
        labels: this.labels,
        datasets: [{
          data: this.values,
          backgroundColor: [
            'rgba(54, 162, 235, 0.8)',   // 예정 - 파란색
            'rgba(75, 192, 192, 0.8)',   // 출근 - 초록색
            'rgba(255, 99, 132, 0.8)'    // 결근 - 빨간색
          ],
          borderColor: [
            'rgba(54, 162, 235, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(255, 99, 132, 1)'
          ],
          borderWidth: 2,
          borderRadius: 4,
          borderSkipped: false
        }]
      };
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
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
                return `${context.label}: ${context.parsed.y}명`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              font: {
                family: "'Noto Sans KR', sans-serif"
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
                size: 12
              }
            },
            grid: {
              display: false
            }
          }
        },
        animation: {
          duration: 1000,
          easing: 'easeOutQuart'
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
  watch: {
    values: {
      handler() {
        this.updateChart();
      },
      deep: true
    }
  },
  methods: {
    initChart() {
      if (!this.$refs.chartCanvas) return;
      
      const ctx = this.$refs.chartCanvas.getContext('2d');
      
      this.chart = new Chart(ctx, {
        type: 'bar',
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

<style src="../css/StatisticsGraph.css"></style> -->