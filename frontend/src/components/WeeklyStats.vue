<template>
  <div class="weekly-stats-container">
    <div class="weekly-stats-header">주차별 온열질환자 및 낙상자 통계</div>
    <div class="chart-container">
      <LineChart
        :chartData="chartData"
        :chartOptions="chartOptions"
      />
    </div>
  </div>
</template>

<script>
import { LineChart } from 'vue-chart-3';
import { Chart, registerables } from 'chart.js';
import '../css/WeeklyStats.css';

// Chart.js 등록
Chart.register(...registerables);

export default {
  name: 'WeeklyStats',
  components: {
    LineChart
  },
  data() {
    return {
      chartData: {
        labels: ['4주 전', '3주 전', '2주 전', '1주 전', '이번주'],
        datasets: [
          {
            label: '온열질환자',
            data: [1, 2, 3, 1, 2], // 이미지의 데이터 사용
            borderColor: '#3490dc',
            backgroundColor: 'rgba(52, 144, 220, 0.2)',
            borderWidth: 2,
            tension: 0.4,
            fill: true
          },
          {
            label: '낙상자',
            data: [2, 1, 3, 4, 2], // 더미 데이터
            borderColor: '#2779bd',
            backgroundColor: 'rgba(39, 121, 189, 0.2)',
            borderWidth: 2,
            tension: 0.4,
            fill: true
          }
        ]
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            top: 5,
            right: 20,
            bottom: 5,
            left: 20
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 5, // 최대값 지정
            ticks: {
              stepSize: 1,
              font: {
                family: "'Noto Sans KR', sans-serif",
                size: 12
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
              display: true,
              color: 'rgba(0, 0, 0, 0.05)'
            }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            align: 'center',
            labels: {
              boxWidth: 10,
              padding: 10,
              font: {
                family: "'Noto Sans KR', sans-serif",
                size: 12
              }
            }
          },
          title: {
            display: false
          },
          tooltip: {
            titleFont: {
              family: "'Noto Sans KR', sans-serif"
            },
            bodyFont: {
              family: "'Noto Sans KR', sans-serif"
            },
            callbacks: {
              label: function(context) {
                return context.dataset.label + ': ' + context.raw + '명';
              }
            }
          }
        }
      }
    };
  }
};
</script>