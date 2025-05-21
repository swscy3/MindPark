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
          <th>위험도</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(worker, index) in displayWorkers" :key="index" :class="getRiskClass(worker.riskLevel)">
          <td>{{ worker.name }}</td>
          <td>{{ worker.temp }}°C</td>
          <td>{{ worker.hr }}bpm</td>
          <td>
            <div class="risk-level-badge" :class="getRiskClass(worker.riskLevel)">
              {{ worker.riskLevel }}
            </div>
          </td>
        </tr>
        <tr v-if="displayWorkers.length === 0">
          <td colspan="4" class="no-data">표시할 데이터가 없습니다.</td>
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
    },
    useDummyData: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      // API 관련 상태
      heatApiData: null,  // 온열질환 API 데이터
      fallApiData: null,  // 낙상 API 데이터
      loading: false,
      error: null,
      
      // 더미 데이터 (API 연결 전 테스트용)
      dummyHeatWorkers: [
        {
          id: 'W001',
          name: '신정우',
          temp: 37.2,
          hr: 81,
          riskLevel: '위험',
          department: '토목팀',
          position: '작업반장'
        },
        {
          id: 'W003',
          name: '김준호',
          temp: 37.8,
          hr: 92,
          riskLevel: '주의',
          department: '철근팀',
          position: '작업자'
        },
        {
          id: 'W005',
          name: '이수민',
          temp: 37.4,
          hr: 88,
          riskLevel: '주의',
          department: '시공팀',
          position: '기사'
        }
      ],
      dummyFallWorkers: [
        {
          id: 'W002',
          name: '박지은',
          temp: 36.8,
          hr: 88,
          riskLevel: '주의',
          department: '전기팀',
          position: '기사'
        },
        {
          id: 'W004',
          name: '장민석',
          temp: 36.9,
          hr: 82,
          riskLevel: '위험',
          department: '구조팀',
          position: '작업자'
        }
      ]
    };
  },
  computed: {
    // 온열질환 API 데이터를 기반으로 작업자 목록 생성
    heatApiWorkers() {
      if (!this.heatApiData) return [];
      
      const { heat_name, heat_temp, heat_hr, heat_risk } = this.heatApiData;
      
      return heat_name.map((name, index) => {
        return {
          name: name,
          temp: heat_temp[index],
          hr: heat_hr[index],
          riskLevel: heat_risk[index],
          lat: this.heatApiData.heat_incident_lat ? this.heatApiData.heat_incident_lat[index] : null,
          lng: this.heatApiData.heat_incident_lng ? this.heatApiData.heat_incident_lng[index] : null
        };
      });
    },
    
    // 낙상 API 데이터를 기반으로 작업자 목록 생성
    fallApiWorkers() {
      if (!this.fallApiData) return [];
      
      const { fall_name, fall_temp, fall_hr, fall_state } = this.fallApiData;
      
      return fall_name.map((name, index) => {
        return {
          name: name,
          temp: fall_temp[index],
          hr: fall_hr[index],
          riskLevel: this.convertFallStateToRiskLevel(fall_state[index]),
          lat: this.fallApiData.fall_incident_lat ? this.fallApiData.fall_incident_lat[index] : null,
          lng: this.fallApiData.fall_incident_lng ? this.fallApiData.fall_incident_lng[index] : null
        };
      });
    },
    
    // 화면에 표시할 데이터 결정
    displayWorkers() {
      // 1. props로 전달된 workers가 있고 더미 데이터를 사용하지 않는 경우
      if (this.workers.length > 0 && !this.useDummyData) {
        return this.workers;
      }
      
      // 2. API 데이터 사용 (더미 데이터를 사용하지 않는 경우)
      if (!this.useDummyData) {
        if (this.riskType === 'heat' && this.heatApiData) {
          return this.heatApiWorkers;
        } else if (this.riskType === 'fall' && this.fallApiData) {
          return this.fallApiWorkers;
        }
      }
      
      // 3. 더미 데이터 사용
      return this.riskType === 'heat' ? this.dummyHeatWorkers : this.dummyFallWorkers;
    }
  },
  mounted() {
    // API를 사용하고 더미 데이터를 사용하지 않는 경우에만 API 호출
    if (!this.useDummyData) {
      if (this.riskType === 'heat') {
        this.fetchHeatIncidentData();
      } else if (this.riskType === 'fall') {
        this.fetchFallIncidentData();
      }
    }
  },
  methods: {
    // 위험도에 따른 CSS 클래스 반환
    getRiskClass(riskLevel) {
      if (riskLevel === '위험') return 'danger';
      if (riskLevel === '주의' || riskLevel === '경고') return 'warning';
      return 'normal';
    },
    
    // 낙상 상태를 위험 수준으로 변환
    convertFallStateToRiskLevel(fallState) {
      if (fallState === '가벼움') return '주의';
      if (fallState === '심각') return '위험';
      return '주의'; // 기본값
    },
    
    // API에서 온열질환 데이터 가져오기
    async fetchHeatIncidentData() {
      this.loading = true;
      this.error = null;
      
      try {
        // API 엔드포인트 호출
        const response = await fetch('/main/heat_incident');
        
        if (!response.ok) {
          throw new Error(`온열질환 API 응답 오류: ${response.status}`);
        }
        
        // JSON 응답을 파싱하여 상태에 저장
        const data = await response.json();
        this.heatApiData = data;
      } catch (err) {
        // 오류 처리
        this.error = `온열질환 데이터를 불러오는 중 오류가 발생했습니다: ${err.message}`;
        console.error(this.error);
      } finally {
        // 로딩 상태 업데이트
        this.loading = false;
      }
    },
    
    // API에서 낙상 데이터 가져오기
    async fetchFallIncidentData() {
      this.loading = true;
      this.error = null;
      
      try {
        // API 엔드포인트 호출
        const response = await fetch('/main/fall_incident');
        
        if (!response.ok) {
          throw new Error(`낙상 API 응답 오류: ${response.status}`);
        }
        
        // JSON 응답을 파싱하여 상태에 저장
        const data = await response.json();
        this.fallApiData = data;
      } catch (err) {
        // 오류 처리
        this.error = `낙상 데이터를 불러오는 중 오류가 발생했습니다: ${err.message}`;
        console.error(this.error);
      } finally {
        // 로딩 상태 업데이트
        this.loading = false;
      }
    }
  }
}
</script>

<style src="../css/RiskWorkersTable.css"></style>