<template>
  <div class="worker-search">
    <div class="header-container">
      <h1>작업자 조회</h1>
    </div>

    <SearchBox 
        v-model="searchTerm"
        placeholder="작업자명 또는 사번 입력"
        :show-icon="true"
        @search="handleSearch"
      />
    
    <div class="table-container">
      <div v-if="loading" class="loading-message">
        데이터를 불러오는 중...
      </div>
      <div v-else-if="workers.length === 0" class="no-data-message">
        조회된 작업자가 없습니다.
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>No</th>
            <th @click="sortTable('name')" class="sortable-header">
              작업자 이름 <span class="sort-icon" :class="{ 'active': sortColumn === 'name' }">{{ sortOrder === 'asc' && sortColumn === 'name' ? '▲' : '▼' }}</span>
            </th>
            <th @click="sortTable('code')" class="sortable-header">
              사번 <span class="sort-icon" :class="{ 'active': sortColumn === 'code' }">{{ sortOrder === 'asc' && sortColumn === 'code' ? '▲' : '▼' }}</span>
            </th>
            <th>부서/소속</th>
            <th>직급</th>
            <th>출근 여부</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(worker, index) in paginatedWorkers" :key="worker.id">
            <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
            <td class="worker-name">{{ worker.name }}</td>
            <td>{{ worker.code }}</td>
            <td>{{ worker.department }}</td>
            <td>{{ worker.position }}</td>
            <td>
              <span class="status-badge" :class="{
                'status-active': worker.status === '출근',
                'status-leave': worker.status === '미출근',
                'status-danger': worker.status === '위험'
              }">
                {{ worker.status }}
              </span>
            </td>
            <td>
              <button class="detail-button" @click="openModal(worker)">
                상세정보
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div class="pagination">
      <button 
        class="pagination-button" 
        :disabled="currentPage === 1" 
        @click="currentPage--"
      >
        &lt;
      </button>
      
      <button 
        v-for="page in totalPages" 
        :key="page" 
        class="pagination-button" 
        :class="{ 'active': currentPage === page }"
        @click="currentPage = page"
      >
        {{ page }}
      </button>
      
      <button 
        class="pagination-button" 
        :disabled="currentPage === totalPages" 
        @click="currentPage++"
      >
        &gt;
      </button>
    </div>

    <!-- 작업자 상세정보 모달 -->
    <WorkerDetailModal 
      :is-visible="isModalVisible"
      :worker="selectedWorker"
      @close="closeModal"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import SearchBox from '../components/SearchBox.vue';
import WorkerDetailModal from '../components/WorkerDetailModal.vue';
import '../css/WorkerSearch.css';

// API에서 가져온 작업자 데이터
const workers = ref([]);
const loading = ref(false);

// SSE 연결 관리
let eventSource = null;

// SSE API 호출 함수
const fetchWorkers = () => {
  loading.value = true;
  
  // 기존 연결이 있으면 닫기
  if (eventSource) {
    eventSource.close();
  }
  
  // 토큰을 쿼리 파라미터로 추가
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0OTMxNDg1MiwianRpIjoiOGU4MWUxNWItOTIwOS00MzI1LThmNjAtNjg4N2JhYzA4ZDVhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IlRFU1RfVVNFUiIsIm5iZiI6MTc0OTMxNDg1MiwiZXhwIjoxNzQ5Njc0ODUyfQ._dvzgnDE-_roLAlHIp2W9FjeplylHy2wlv8KTqjQt-Y';
  const url = `http://orion.mokpo.ac.kr:8485/api/web/emp/list/stream?token=${token}`;
  
  try {
    // EventSource 생성
    eventSource = new EventSource(url);
    
    // 연결 성공
    eventSource.onopen = (event) => {
      console.log('SSE 연결 성공:', event);
    };
    
    // 메시지 수신
    eventSource.onmessage = (event) => {
      try {
        console.log('SSE 원본 데이터:', event.data);
        const responseData = JSON.parse(event.data);
        
        console.log('SSE 파싱된 데이터:', responseData);
        console.log('직원 데이터:', responseData.data?.employees);
        
        if (responseData.status === 'success' && responseData.data?.employees) {
          // 새로운 API 구조에 맞게 데이터 변환
          workers.value = responseData.data.employees.map((employee, index) => ({
            id: index + 1,
            name: employee.name,
            code: employee.emp_id,
            department: employee.department,
            position: employee.position,
            status: employee.attendance_status === '미출근' ? '미출근' : '출근',
            // 원본 API 데이터 보존
            originalData: employee
          }));
          
          console.log('변환된 작업자 데이터:', workers.value);
          loading.value = false;
        } else {
          console.log('SSE 응답 구조가 예상과 다름:', responseData);
        }
      } catch (parseError) {
        console.error('SSE 데이터 파싱 오류:', parseError);
        console.log('파싱 실패한 원본 데이터:', event.data);
      }
    };
    
    // 에러 처리
    eventSource.onerror = (error) => {
      console.error('SSE 연결 오류:', error);
      console.error('EventSource readyState:', eventSource.readyState);
      
      loading.value = false;
      
      // 연결 재시도 또는 빈 배열 유지
      setTimeout(() => {
        console.log('SSE 연결 재시도...');
        if (eventSource.readyState === EventSource.CLOSED) {
          // 빈 배열 유지
          workers.value = [];
        }
      }, 3000);
    };
    
  } catch (error) {
    console.error('SSE 초기화 오류:', error);
    loading.value = false;
    workers.value = [];
  }
};

// 컴포넌트 마운트 시 데이터 로드
onMounted(() => {
  fetchWorkers();
});

// 컴포넌트 언마운트 시 SSE 연결 해제
onUnmounted(() => {
  if (eventSource) {
    console.log('SSE 연결 해제');
    eventSource.close();
    eventSource = null;
  }
});

const searchTerm = ref('');
const currentPage = ref(1);
const pageSize = 10;
const sortColumn = ref('name');
const sortOrder = ref('asc');

// 모달 관련 상태
const isModalVisible = ref(false);
const selectedWorker = ref({});

// 검색 버튼 클릭 또는 엔터키 처리
const handleSearch = () => {
  // 현재는 실시간 검색이므로 추가 동작 불필요
};

// 모달 열기 - 개별 직원 상세 API 호출
const openModal = async (worker) => {
  console.log('=== 모달 열기 시작 ===');
  console.log('선택된 작업자:', worker);
  console.log('작업자 코드:', worker.code);
  
  try {
    // 상세 정보 API 호출
    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0OTMxNDg1MiwianRpIjoiOGU4MWUxNWItOTIwOS00MzI1LThmNjAtNjg4N2JhYzA4ZDVhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IlRFU1RfVVNFUiIsIm5iZiI6MTc0OTMxNDg1MiwiZXhwIjoxNzQ5Njc0ODUyfQ._dvzgnDE-_roLAlHIp2W9FjeplylHy2wlv8KTqjQt-Y';
    const detailUrl = `http://orion.mokpo.ac.kr:8485/api/web/emp/${worker.code}/detail?token=${token}`;
    
    console.log('호출할 API URL:', detailUrl);
    
    // fetch로 API 호출
    console.log('API 호출 시작...');
    const response = await fetch(detailUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    
    console.log('응답 상태:', response.status);
    console.log('응답 OK:', response.ok);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const detailData = await response.json();
    console.log('=== 상세 API 응답 전체 ===');
    console.log(JSON.stringify(detailData, null, 2));
    
    if (detailData.status === 'success' && detailData.data) {
      const detail = detailData.data;
      console.log('=== 상세 데이터 ===');
      console.log('이름:', detail.name);
      console.log('나이:', detail.age);
      console.log('성별:', detail.gender);
      console.log('긴급연락처:', detail.emergency_contact);
      
      selectedWorker.value = {
        // 기본 정보 (목록 + 상세 API 조합)
        id: worker.id,
        name: detail.name || worker.name,
        code: worker.code,
        department: worker.department,
        position: worker.position,
        status: worker.status,
        
        // 상세 정보 (상세 API에서 제공)
        gender: detail.gender === 'M' ? '남성' : detail.gender === 'F' ? '여성' : '미제공',
        age: detail.age ? detail.age.toString() : '미제공',
        
        // 생체 정보 (상세 API에서 제공)
        heartRate: detail.heart_rate ? detail.heart_rate.toString() : '미측정',
        oxygenSaturation: detail.spo2 ? detail.spo2.toString() : '미측정',
        temperature: detail.temperature ? detail.temperature.toString() : '미측정',
        steps: detail.steps ? detail.steps.toString() : '미측정',
        
        // 디바이스 정보 (상세 API에서 제공)
        deviceLocation: detail.device_name || '미연결',
        batteryLevel: detail.battery_level ? detail.battery_level.toString() : '미측정',
        
        // 긴급연락처 정보 (상세 API에서 제공) - 파싱 개선
        emergencyContact: detail.emergency_contact ? (() => {
          const contact = detail.emergency_contact;
          console.log('긴급연락처 원본:', contact);
          
          // "김남길 (형제자매) - 010-9780-2846" 형태 파싱
          const nameMatch = contact.split(' (')[0];
          const relationMatch = contact.match(/\(([^)]+)\)/);
          const phoneMatch = contact.match(/- (.+)$/);
          
          const parsed = {
            name: nameMatch || '미제공',
            relation: relationMatch ? relationMatch[1] : '미제공',
            phone: phoneMatch ? phoneMatch[1] : '미제공'
          };
          
          console.log('파싱된 긴급연락처:', parsed);
          return parsed;
        })() : {
          name: '미제공',
          relation: '미제공', 
          phone: '미제공'
        },
        
        // 위치 정보 (상세 API에서 제공)
        location: {
          latitude: detail.latitude,
          longitude: detail.longitude,
          building: detail.latitude && detail.longitude ? '위치 확인됨' : '위치 미확인',
          floor: '미제공',
          room: '미제공'
        }
      };
      
      console.log('=== 최종 모달 데이터 ===');
      console.log(JSON.stringify(selectedWorker.value, null, 2));
      console.log('모달 표시 상태 변경 전:', isModalVisible.value);
      
      isModalVisible.value = true;
      
      console.log('모달 표시 상태 변경 후:', isModalVisible.value);
      console.log('=== 모달 열기 완료 ===');
    } else {
      console.error('=== API 응답 구조 오류 ===');
      console.error('status:', detailData.status);
      console.error('data 존재 여부:', !!detailData.data);
      console.error('전체 응답:', detailData);
      openBasicModal(worker);
    }
  } catch (error) {
    console.error('=== API 호출 중 오류 발생 ===');
    console.error('오류 유형:', error.name);
    console.error('오류 메시지:', error.message);
    console.error('전체 오류:', error);
    openBasicModal(worker);
  }
};

// 기본 정보만으로 모달 열기 (API 실패 시)
const openBasicModal = (worker) => {
  console.log('=== 기본 모달 열기 ===');
  console.log('기본 정보로 모달 생성:', worker);
  
  selectedWorker.value = {
    id: worker.id,
    name: worker.name,
    code: worker.code,
    department: worker.department,
    position: worker.position,
    status: worker.status,
    gender: '조회 실패',
    age: '조회 실패',
    heartRate: '조회 실패',
    oxygenSaturation: '조회 실패',
    temperature: '조회 실패',
    steps: '조회 실패',
    deviceLocation: '조회 실패',
    batteryLevel: '조회 실패',
    emergencyContact: {
      name: '조회 실패',
      relation: '조회 실패',
      phone: '조회 실패'
    },
    location: {
      latitude: null,
      longitude: null,
      building: '조회 실패',
      floor: '조회 실패',
      room: '조회 실패'
    }
  };
  
  console.log('기본 모달 데이터:', selectedWorker.value);
  console.log('기본 모달 표시 상태 변경 전:', isModalVisible.value);
  
  isModalVisible.value = true;
  
  console.log('기본 모달 표시 상태 변경 후:', isModalVisible.value);
  console.log('=== 기본 모달 열기 완료 ===');
};

// 모달 닫기
const closeModal = () => {
  isModalVisible.value = false;
  selectedWorker.value = {}; // 모달 닫을 때 데이터 초기화
};

// 정렬 기능
const sortTable = (column) => {
  if(sortColumn.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortOrder.value = 'asc';
  }
};

// 검색된 작업자 필터링
const filteredWorkers = computed(() => {
  if (!searchTerm.value) {
    return workers.value;
  }
  
  const term = searchTerm.value.toLowerCase();
  return workers.value.filter(worker => 
    worker.name.toLowerCase().includes(term) || 
    worker.code.includes(term)
  );
});

// 페이지네이션을 위한 계산된 속성
const totalPages = computed(() => {
  return Math.ceil(filteredWorkers.value.length / pageSize);
});

// 정렬 및 페이지네이션, 검색 적용된 작업자 데이터
const paginatedWorkers = computed(() => {
  // 검색 필터링 및 정렬 로직
  const sorted = [...filteredWorkers.value].sort((a, b) => {
    const aValue = a[sortColumn.value];
    const bValue = b[sortColumn.value];
    
    if(sortOrder.value === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  
  // 페이지네이션 로직
  const start = (currentPage.value - 1) * pageSize;
  const end = start + pageSize;
  return sorted.slice(start, end);
});

// 검색어가 변경되면 첫 페이지로 이동
watch(searchTerm, () => {
  currentPage.value = 1;
});
</script>