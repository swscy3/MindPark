<template>
  <div class="risk-table-container">
    <div class="table-header">
      <h3>{{ tableTitle }} {{ riskType === 'heat' ? '온열질환' : '낙상' }} 위험</h3>
      <div v-if="showSOS" class="sos-badge">SOS 현황 {{ sosCount }}</div>
    </div>
    <table class="risk-table">
      <thead>
        <tr>
          <th>사원명</th>
          <th>체온</th>
          <th>심박수</th>
          <th>호흡수</th>
          <th>위험도</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(worker, index) in displayWorkers" :key="index" :class="getRiskClass(worker.risk_level)">
          <td>{{ worker.name }}</td>
          <td>{{ worker.vitals?.temperature || 'N/A' }}°C</td>
          <td>{{ worker.vitals?.heart_rate || 'N/A' }}bpm</td>
          <td>{{ worker.vitals?.respiration || 'N/A' }}rpm</td>
          <td>
            <div class="risk-level-badge" :class="getRiskClass(worker.risk_level)">
              {{ worker.risk_level }}
            </div>
          </td>
        </tr>
        <tr v-if="displayWorkers.length === 0">
          <td colspan="5" class="no-data">표시할 데이터가 없습니다.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'RiskWorkersTable',
  props: {
    tableTitle: {
      type: String,
      default: '현재 감지'
    },
    workers: {
      type: Array,
      default: () => []
    },
    showSOS: {
      type: Boolean,
      default: false
    },
    sosCount: {
      type: Number,
      default: 0
    },
    riskType: {
      type: String,
      default: 'heat' // 'heat' 또는 'fall'
    }
  },
  computed: {
    // 화면에 표시할 데이터 (props로 받은 workers 사용)
    displayWorkers() {
      return this.workers || [];
    }
  },
  methods: {
    // 위험도에 따른 CSS 클래스 반환
    getRiskClass(riskLevel) {
      if (riskLevel === '위험') return 'danger';
      if (riskLevel === '주의' || riskLevel === '경고') return 'warning';
      return 'normal';
    }
  }
}
</script>

<style src="../css/RiskWorkersTable.css"></style>