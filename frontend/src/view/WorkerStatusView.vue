<template>
  <div class="worker-status">
    <div class="tabs">
      <div class="tab" :class="{ active: activeTab === 'danger' }" @click="activeTab = 'danger'">안전 위험</div>
      <div class="tab" :class="{ active: activeTab === 'caution' }" @click="activeTab = 'caution'">안전 주의</div>
    </div>
    
    <div v-if="loading" class="loading-message">
      데이터를 불러오는 중...
    </div>
    
    <div v-else-if="filteredWorkers.length === 0" class="no-data-message">
      해당 상태의 작업자가 없습니다.
    </div>
    
    <div v-else class="worker-container">
      <div class="worker-row" v-for="(group, groupIndex) in paginatedGroups" :key="groupIndex">
        <div v-for="(worker, workerIndex) in group" :key="worker.id" class="worker-column">
          <div class="worker-card" :class="{ 'normal-card': worker.status !== 'danger' }">
            <div class="status-indicator" v-if="worker.status === 'danger'">위험</div>
            <div class="caution-indicator" v-if="worker.status === 'caution'">주의</div>
            <div class="worker-info">
              <div class="profile-image">
                <img :src="worker.profileImage || '/img/default-profile.png'" :alt="`${worker.name} 프로필`">
              </div>
              <div class="info-text">
                <div class="worker-name">{{ worker.name }}</div>
                <div class="worker-age">{{ worker.age }}세, {{ worker.gender }}</div>
                <div class="worker-phone">보호자 연락처:<br> {{ worker.phone }}</div>
              </div>
            </div>
            
            <div class="detail-section">
              <div class="section-title">생체 정보</div>
              <div class="detail-item">
                <div class="detail-label">심박수</div>
                <div class="detail-value">{{ worker.vitalSigns.heartRate }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">산소포화도</div>
                <div class="detail-value">{{ worker.vitalSigns.oxygenSaturation }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">체온</div>
                <div class="detail-value">{{ worker.vitalSigns.bodyTemperature }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">걸음수</div>
                <div class="detail-value">{{ worker.vitalSigns.walk }}</div>
              </div>
            </div>
            
            <div class="collapsible-section">
              <div class="collapsible-header" @click="toggleDeviceInfo(worker.id)">
                <div class="section-title">디바이스 정보</div>
                <div class="collapsible-icon" :class="{ 'is-open': expandedDevices.includes(worker.id) }">
                  <span>&#9660;</span>
                </div>
              </div>
              <div class="collapsible-content" :class="{ 'is-open': expandedDevices.includes(worker.id) }">
                <div class="detail-item">
                  <div class="detail-label">워치 이름</div>
                  <div class="detail-value">{{ worker.device.name }}</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">배터리 상태</div>
                  <div class="detail-value">{{ worker.device.batteryStatus }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 커스텀 페이지네이션 -->
    <Pagination 
      v-if="!loading && filteredWorkers.length > 0"
      :current-page="currentPage"
      :total-items="filteredWorkers.length"
      :items-per-page="workersPerPage"
      @page-change="handlePageChange"
    />
  </div>
</template>

<script>
import Pagination from '../components/Pagination.vue';

export default {
  name: 'WorkerStatus',
  components: {
    Pagination
  },
  data() {
    return {
      activeTab: 'danger',
      currentPage: 1,
      workersPerPage: 10, // 한 페이지에 10명 (2행 5열)
      workersPerRow: 5,   // 한 행에 5명
      expandedDevices: [], // 확장된 디바이스 정보를 추적하는 배열
      workers: [],
      loading: false,
      eventSource: null  // SSE 연결 객체 추가
    };
  },
  computed: {
    filteredWorkers() {
      // 이제 각 탭마다 해당 API에서 데이터를 받아오므로 
      // 별도 필터링 없이 모든 workers를 반환
      return this.workers;
    },
    
    // 페이지네이션을 위한 작업자 목록 슬라이싱
    paginatedWorkers() {
      const startIndex = (this.currentPage - 1) * this.workersPerPage;
      const endIndex = startIndex + this.workersPerPage;
      
      return this.filteredWorkers.slice(startIndex, endIndex);
    },
    
    // 행 별로 작업자 배열 분할
    paginatedGroups() {
      const groups = [];
      const workersInPage = this.paginatedWorkers;
      
      // 한 행에 workersPerRow명씩 표시
      for (let i = 0; i < workersInPage.length; i += this.workersPerRow) {
        groups.push(workersInPage.slice(i, i + this.workersPerRow));
      }
      
      return groups;
    }
  },
  async mounted() {
    await this.fetchWorkers();
  },
  beforeUnmount() {
    // 컴포넌트가 언마운트될 때 SSE 연결 정리
    if (this.eventSource) {
      console.log('WorkerStatus SSE 연결 종료');
      this.eventSource.close();
      this.eventSource = null;
    }
  },
  methods: {
    handlePageChange(page) {
      this.currentPage = page;
    },
    async fetchWorkers() {
      this.loading = true;
      
      // 기존 SSE 연결이 있다면 종료
      if (this.eventSource) {
        this.eventSource.close();
      }
      
      try {
        const token = localStorage.getItem('token');
        
        // activeTab에 따라 다른 엔드포인트 사용
        let endpoint = '';
        if (this.activeTab === 'danger') {
          endpoint = 'danger-employees';
        } else if (this.activeTab === 'caution') {
          endpoint = 'caution-employees';
        }
        
        const url = `http://orion.mokpo.ac.kr:8485/api/web/safety/${endpoint}/stream?token=${token}`;
        
        console.log(`WorkerStatus SSE 연결 시작 (${this.activeTab}):`, url);
        this.eventSource = new EventSource(url);
        
        this.eventSource.onopen = () => {
          console.log(`WorkerStatus SSE 연결 성공 (${this.activeTab})`);
          this.loading = false;
        };
        
        this.eventSource.onmessage = (event) => {
          try {
            console.log(`WorkerStatus SSE 데이터 수신 (${this.activeTab}):`, event.data);
            
            if (event.data.trim() === '') {
              console.log('빈 데이터 수신, 무시');
              return;
            }
            
            const data = JSON.parse(event.data);
            console.log(`WorkerStatus 파싱된 데이터 (${this.activeTab}):`, data);
            
            if (data.status === 'success' && data.data?.employees) {
              // API 데이터를 기존 구조에 맞게 변환
              this.workers = data.data.employees.map((employee, index) => ({
                id: index + 1,
                name: employee.basic_info.name,
                age: `만 ${employee.basic_info.age}`,
                gender: employee.basic_info.gender === 'M' ? '남' : '여',
                phone: employee.emergency_contact.phone,
                status: this.determineStatus(employee),
                profileImage: employee.basic_info.picture 
                  ? `http://orion.mokpo.ac.kr:8485${employee.basic_info.picture}` 
                  : '',
                vitalSigns: {
                  heartRate: `${employee.current_vitals.heart_rate}bpm`,
                  oxygenSaturation: `${employee.current_vitals.spo2}%`,
                  bodyTemperature: `${employee.current_vitals.temperature}°C`,
                  walk: employee.current_vitals.steps.toLocaleString()
                },
                device: {
                  name: employee.device_info.device_name,
                  batteryStatus: `${employee.device_info.battery_level}%`
                },
                originalData: employee
              }));
              
              console.log(`WorkerStatus 데이터 업데이트 완료 (${this.activeTab}):`, this.workers);
            } else {
              console.log(`WorkerStatus 연결 확인 메시지 또는 예상과 다른 데이터 구조 (${this.activeTab})`);
            }
            
          } catch (error) {
            console.error(`WorkerStatus SSE 데이터 파싱 오류 (${this.activeTab}):`, error);
          }
        };
        
        this.eventSource.onerror = (error) => {
          console.error(`WorkerStatus SSE 연결 오류 (${this.activeTab}):`, error);
          this.loading = false;
          
          // 재연결 시도
          setTimeout(() => {
            if (this.eventSource?.readyState === EventSource.CLOSED) {
              console.log(`WorkerStatus SSE 재연결 시도 (${this.activeTab})...`);
              this.fetchWorkers();
            }
          }, 5000);
        };
        
      } catch (error) {
        console.error(`WorkerStatus SSE 연결 생성 실패 (${this.activeTab}):`, error);
        this.loading = false;
      }
    },
    
    determineStatus(employee) {
      // API의 risk_info를 기반으로 상태 결정
      if (employee.risk_info) {
        if (employee.risk_info.risk_level === '위험') {
          return 'danger';
        } else if (employee.risk_info.risk_level === '주의') {
          return 'caution';
        }
      }
      
      // 생체 신호를 기반으로 상태 판단
      const vitals = employee.current_vitals;
      const isHighHeartRate = vitals.heart_rate > 100;
      const isLowSpo2 = vitals.spo2 < 95;
      const isHighTemp = vitals.temperature > 37.5;
      
      if ((isHighHeartRate && isLowSpo2) || isHighTemp) {
        return 'danger';
      } else if (isHighHeartRate || isLowSpo2 || vitals.temperature > 37.0) {
        return 'caution';
      }
      
      return 'normal';
    },
    
    toggleDeviceInfo(workerId) {
      if (this.expandedDevices.includes(workerId)) {
        // 이미 확장된 경우, 배열에서 제거 (접기)
        this.expandedDevices = this.expandedDevices.filter(id => id !== workerId);
      } else {
        // 아직 확장되지 않은 경우, 배열에 추가 (펼치기)
        this.expandedDevices.push(workerId);
      }
    }
  },
  watch: {
    // activeTab이 변경될 때마다 currentPage를 1로 리셋하고 새로운 API 호출
    activeTab() {
      this.currentPage = 1;
      this.fetchWorkers(); // 탭 변경 시 새로운 API 엔드포인트로 연결
    }
  }
};
</script>

<style src="../css/WorkerStatus.css"></style>