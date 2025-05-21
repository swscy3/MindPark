<template>
  <div class="worker-search">
    <div class="header-container">
      <h1>작업자 조회</h1>
      
      <div class="search-container">
        <input
          type="text"
          placeholder="작업자명 또는 사번 입력"
          v-model="searchTerm"
        />
        <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>
    
    <div class="table-container">
      <table>
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
                'status-absent': worker.status === '결근',
                'status-leave': worker.status === '휴무'
              }">
                {{ worker.status }}
              </span>
            </td>
            <td>
              <button class="detail-button">
                세부 내용
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
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import '../css/WorkerSearch.css';

// Sample worker data
const workers = ref([
  { id: 1, name: '신창우', code: '223714', department: '티켓팅', position: '팀장', status: '출근' },
  { id: 2, name: '박지은', code: '223711', department: '품질관리팀', position: '사원', status: '출근' },
  { id: 3, name: '정희주', code: '223714', department: '관리팀', position: '사원', status: '휴무' },
  { id: 4, name: '김민준', code: '223715', department: '개발팀', position: '과장', status: '출근' },
  { id: 5, name: '이서연', code: '223716', department: '디자인팀', position: '주임', status: '휴무' },
  { id: 6, name: '최준호', code: '223717', department: '마케팅팀', position: '대리', status: '출근' },
  { id: 7, name: '강지원', code: '223718', department: '인사팀', position: '사원', status: '출근' },
  { id: 8, name: '윤소율', code: '223719', department: '회계팀', position: '과장', status: '출근' },
  { id: 9, name: '장현우', code: '223720', department: '영업팀', position: '대리', status: '휴무' },
  { id: 10, name: '한미래', code: '223721', department: '기획팀', position: '사원', status: '출근' },
  { id: 11, name: '오태양', code: '223722', department: '고객지원팀', position: '팀장', status: '출근' },
  { id: 12, name: '임하늘', code: '223723', department: '연구팀', position: '연구원', status: '휴무' },
  { id: 13, name: '서은별', code: '223724', department: '품질관리팀', position: '주임', status: '출근' },
  { id: 14, name: '배도현', code: '223725', department: '생산팀', position: '대리', status: '출근' },
  { id: 15, name: '홍길동', code: '223726', department: '보안팀', position: '과장', status: '휴무' },
]);

const searchTerm = ref('');
const currentPage = ref(1);
const pageSize = 10;
const sortColumn = ref('name');
const sortOrder = ref('asc');

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