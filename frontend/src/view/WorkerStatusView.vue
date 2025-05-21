<template>
  <div class="worker-status">
    <div class="tabs">
      <div class="tab" :class="{ active: activeTab === 'danger' }" @click="activeTab = 'danger'">안전 위험</div>
      <div class="tab" :class="{ active: activeTab === 'caution' }" @click="activeTab = 'caution'">안전 주의</div>
    </div>
    
    <div class="worker-container">
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
                <div class="worker-phone">{{ worker.phone }}</div>
                <div class="worker-location">위치</div>
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
                <div class="detail-label">혈압</div>
                <div class="detail-value">{{ worker.vitalSigns.bloodPressure }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">체온</div>
                <div class="detail-value">{{ worker.vitalSigns.bodyTemperature }}</div>
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
    
    <div class="pagination-controls">
      <div class="page-info">{{ currentPage }} / {{ totalPages }} 페이지</div>
      <div class="pagination-buttons">
        <button class="pagination-button" @click="goToPage(1)" :disabled="currentPage === 1">처음</button>
        <button class="pagination-button" @click="prevPage" :disabled="currentPage === 1">←</button>
        <div class="page-numbers">
          <button 
            v-for="page in displayedPages" 
            :key="page" 
            @click="goToPage(page)" 
            :class="{ 'active-page': currentPage === page }"
            class="page-number"
          >
            {{ page }}
          </button>
        </div>
        <button class="pagination-button" @click="nextPage" :disabled="currentPage === totalPages">→</button>
        <button class="pagination-button" @click="goToPage(totalPages)" :disabled="currentPage === totalPages">마지막</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WorkerStatus',
  data() {
    return {
      activeTab: 'danger',
      currentPage: 1,
      workersPerPage: 10, // 한 페이지에 10명 (2행 5열)
      workersPerRow: 5,   // 한 행에 5명
      expandedDevices: [], // 확장된 디바이스 정보를 추적하는 배열
      workers: [
        // 위험 상태 근로자 (14명)
        {
          id: 1,
          name: '박지은',
          age: '만 23',
          gender: '여',
          phone: '010-2237-0011',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '112bpm',
            oxygenSaturation: '90%',
            bloodPressure: '145mmHg',
            bodyTemperature: '38.5°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '85%'
          }
        },
        {
          id: 2,
          name: '이민준',
          age: '만 42',
          gender: '남',
          phone: '010-9876-5432',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '110bpm',
            oxygenSaturation: '92%',
            bloodPressure: '135mmHg',
            bodyTemperature: '38.2°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '25%'
          }
        },
        {
          id: 3,
          name: '최서연',
          age: '만 29',
          gender: '여',
          phone: '010-1122-3344',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '115bpm',
            oxygenSaturation: '91%',
            bloodPressure: '140mmHg',
            bodyTemperature: '38.7°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '65%'
          }
        },
        {
          id: 4,
          name: '송현우',
          age: '만 38',
          gender: '남',
          phone: '010-3344-5566',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '105bpm',
            oxygenSaturation: '92%',
            bloodPressure: '138mmHg',
            bodyTemperature: '38.0°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '18%'
          }
        },
        {
          id: 5,
          name: '양지원',
          age: '만 24',
          gender: '여',
          phone: '010-5566-7788',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '112bpm',
            oxygenSaturation: '90%',
            bloodPressure: '145mmHg',
            bodyTemperature: '38.5°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '32%'
          }
        },
        {
          id: 6,
          name: '안태현',
          age: '만 36',
          gender: '남',
          phone: '010-7788-9900',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '108bpm',
            oxygenSaturation: '91%',
            bloodPressure: '142mmHg',
            bodyTemperature: '38.3°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '22%'
          }
        },
        {
          id: 7,
          name: '김민지',
          age: '만 22',
          gender: '여',
          phone: '010-9900-1122',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '114bpm',
            oxygenSaturation: '89%',
            bloodPressure: '148mmHg',
            bodyTemperature: '38.9°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '28%'
          }
        },
        {
          id: 8,
          name: '송재호',
          age: '만 37',
          gender: '남',
          phone: '010-1122-3344',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '107bpm',
            oxygenSaturation: '91%',
            bloodPressure: '140mmHg',
            bodyTemperature: '38.4°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '20%'
          }
        },
        {
          id: 9,
          name: '양미래',
          age: '만 24',
          gender: '여',
          phone: '010-3344-5566',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '113bpm',
            oxygenSaturation: '90%',
            bloodPressure: '146mmHg',
            bodyTemperature: '38.6°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '30%'
          }
        },
        {
          id: 10,
          name: '김하늘',
          age: '만 29',
          gender: '여',
          phone: '010-2233-4455',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '118bpm',
            oxygenSaturation: '88%',
            bloodPressure: '150mmHg',
            bodyTemperature: '38.8°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '25%'
          }
        },
        {
          id: 11,
          name: '정우진',
          age: '만 33',
          gender: '남',
          phone: '010-6677-8899',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '106bpm',
            oxygenSaturation: '90%',
            bloodPressure: '144mmHg',
            bodyTemperature: '38.3°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '31%'
          }
        },
        {
          id: 12,
          name: '고은영',
          age: '만 26',
          gender: '여',
          phone: '010-3355-7788',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '110bpm',
            oxygenSaturation: '89%',
            bloodPressure: '147mmHg',
            bodyTemperature: '38.7°C'
          },
          device: {
            name: '스마트워치 C',
            batteryStatus: '23%'
          }
        },
        {
          id: 13,
          name: '윤성민',
          age: '만 31',
          gender: '남',
          phone: '010-9988-7766',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '108bpm',
            oxygenSaturation: '91%',
            bloodPressure: '139mmHg',
            bodyTemperature: '38.1°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '42%'
          }
        },
        {
          id: 14,
          name: '장서현',
          age: '만 28',
          gender: '여',
          phone: '010-1122-3355',
          status: 'danger',
          profileImage: '',
          vitalSigns: {
            heartRate: '115bpm',
            oxygenSaturation: '90%',
            bloodPressure: '143mmHg',
            bodyTemperature: '38.4°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '19%'
          }
        },
        
        // 주의 상태 근로자 (13명)
        {
          id: 15,
          name: '김영호',
          age: '만 35',
          gender: '남',
          phone: '010-3456-7890',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '88bpm',
            oxygenSaturation: '97%',
            bloodPressure: '120mmHg',
            bodyTemperature: '37.1°C'
          },
          device: {
            name: '스마트워치 C',
            batteryStatus: '45%'
          }
        },
        {
          id: 16,
          name: '한지민',
          age: '만 27',
          gender: '여',
          phone: '010-9900-1122',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '95bpm',
            oxygenSaturation: '94%',
            bloodPressure: '125mmHg',
            bodyTemperature: '37.5°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '42%'
          }
        },
        {
          id: 17,
          name: '강민호',
          age: '만 33',
          gender: '남',
          phone: '010-1122-3344',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '92bpm',
            oxygenSaturation: '93%',
            bloodPressure: '130mmHg',
            bodyTemperature: '37.4°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '55%'
          }
        },
        {
          id: 18,
          name: '유하은',
          age: '만 26',
          gender: '여',
          phone: '010-3344-5566',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '94bpm',
            oxygenSaturation: '94%',
            bloodPressure: '128mmHg',
            bodyTemperature: '37.3°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '48%'
          }
        },
        {
          id: 19,
          name: '한소율',
          age: '만 30',
          gender: '여',
          phone: '010-7788-9900',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '93bpm',
            oxygenSaturation: '94%',
            bloodPressure: '127mmHg',
            bodyTemperature: '37.4°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '51%'
          }
        },
        {
          id: 20,
          name: '강태준',
          age: '만 32',
          gender: '남',
          phone: '010-9900-1122',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '90bpm',
            oxygenSaturation: '93%',
            bloodPressure: '131mmHg',
            bodyTemperature: '37.3°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '60%'
          }
        },
        {
          id: 21,
          name: '유지은',
          age: '만 25',
          gender: '여',
          phone: '010-1122-3344',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '92bpm',
            oxygenSaturation: '94%',
            bloodPressure: '126mmHg',
            bodyTemperature: '37.2°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '54%'
          }
        },
        {
          id: 22,
          name: '이준호',
          age: '만 35',
          gender: '남', 
          phone: '010-6677-8899',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '95bpm',
            oxygenSaturation: '92%',
            bloodPressure: '133mmHg',
            bodyTemperature: '37.6°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '45%'
          }
        },
        {
          id: 23,
          name: '박지훈',
          age: '만 29',
          gender: '남',
          phone: '010-2255-6677',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '91bpm',
            oxygenSaturation: '93%',
            bloodPressure: '129mmHg',
            bodyTemperature: '37.3°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '49%'
          }
        },
        {
          id: 24,
          name: '최다혜',
          age: '만 31',
          gender: '여',
          phone: '010-8877-6655',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '89bpm',
            oxygenSaturation: '94%',
            bloodPressure: '124mmHg',
            bodyTemperature: '37.0°C'
          },
          device: {
            name: '스마트워치 C',
            batteryStatus: '62%'
          }
        },
        {
          id: 25,
          name: '문승우',
          age: '만 34',
          gender: '남',
          phone: '010-3366-9988',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '87bpm',
            oxygenSaturation: '95%',
            bloodPressure: '122mmHg',
            bodyTemperature: '37.2°C'
          },
          device: {
            name: '스마트워치 A',
            batteryStatus: '58%'
          }
        },
        {
          id: 26,
          name: '임수진',
          age: '만 27',
          gender: '여',
          phone: '010-4433-2211',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '93bpm',
            oxygenSaturation: '93%',
            bloodPressure: '127mmHg',
            bodyTemperature: '37.4°C'
          },
          device: {
            name: '스마트워치 B',
            batteryStatus: '51%'
          }
        },
        {
          id: 27,
          name: '손민재',
          age: '만 28',
          gender: '남',
          phone: '010-9911-2233',
          status: 'caution',
          profileImage: '',
          vitalSigns: {
            heartRate: '88bpm',
            oxygenSaturation: '96%',
            bloodPressure: '123mmHg',
            bodyTemperature: '37.1°C'
          },
          device: {
            name: '스마트워치 C',
            batteryStatus: '66%'
          }
        }
      ]
    };
  },
  computed: {
    filteredWorkers() {
      let filtered = this.workers;
      
      // 탭에 따라 필터링
      if (this.activeTab === 'danger') {
        filtered = filtered.filter(worker => worker.status === 'danger');
      } else if (this.activeTab === 'caution') {
        filtered = filtered.filter(worker => worker.status === 'caution');
      }
      
      return filtered;
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
    },
    
    totalPages() {
      return Math.ceil(this.filteredWorkers.length / this.workersPerPage);
    },
    
    // 페이지 네비게이션에 표시할 페이지 번호
    displayedPages() {
      const pages = [];
      const maxPageButtons = 5; // 한 번에 표시할 페이지 버튼 수
      
      let startPage = Math.max(1, this.currentPage - Math.floor(maxPageButtons / 2));
      let endPage = startPage + maxPageButtons - 1;
      
      if (endPage > this.totalPages) {
        endPage = this.totalPages;
        startPage = Math.max(1, endPage - maxPageButtons + 1);
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      
      return pages;
    }
  },
  methods: {
    toggleDeviceInfo(workerId) {
      if (this.expandedDevices.includes(workerId)) {
        // 이미 확장된 경우, 배열에서 제거 (접기)
        this.expandedDevices = this.expandedDevices.filter(id => id !== workerId);
      } else {
        // 아직 확장되지 않은 경우, 배열에 추가 (펼치기)
        this.expandedDevices.push(workerId);
      }
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
      }
    },
  },
    watch: {
    // activeTab이 변경될 때마다 currentPage를 1로 리셋
    activeTab() {
      this.currentPage = 1;
    }
  }
};
</script>

<style src="../css/WorkerStatus.css"></style>