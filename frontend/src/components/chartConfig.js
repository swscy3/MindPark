// 푸른 계열 색상 팔레트
export const blueColors = {
  primary: '#3490dc',
  secondary: '#2779bd',
  tertiary: '#4FC3F7',
  light: '#BBDEFB',
  dark: '#0D47A1'
};

// 기본 차트 옵션 (bar, line 차트용)
export const defaultChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  aspectRatio: 1,
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
          family: "'Noto Sans KR', sans-serif"
        }
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      }
    }
  },
  plugins: {
    legend: {
      position: 'top',
      labels: {
        font: {
          family: "'Noto Sans KR', sans-serif"
        }
      }
    },
    tooltip: {
      titleFont: {
        family: "'Noto Sans KR', sans-serif"
      },
      bodyFont: {
        family: "'Noto Sans KR', sans-serif"
      }
    }
  }
};

// doughnut 차트 전용 옵션 추가
export const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      titleFont: {
        family: "'Noto Sans KR', sans-serif"
      },
      bodyFont: {
        family: "'Noto Sans KR', sans-serif"
      }
    }
  }
};