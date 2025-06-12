<template>
  <div class="pagination">
    <button 
      class="pagination-button" 
      :disabled="currentPage === 1" 
      @click="goToPage(currentPage - 1)"
    >
      &lt;
    </button>
    
    <button 
      v-for="page in totalPages" 
      :key="page" 
      class="pagination-button" 
      :class="{ 'active': currentPage === page }"
      @click="goToPage(page)"
    >
      {{ page }}
    </button>
    
    <button 
      class="pagination-button" 
      :disabled="currentPage === totalPages" 
      @click="goToPage(currentPage + 1)"
    >
      &gt;
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// Props 정의
const props = defineProps({
  currentPage: {
    type: Number,
    required: true,
    default: 1
  },
  totalItems: {
    type: Number,
    required: true,
    default: 0
  },
  itemsPerPage: {
    type: Number,
    default: 10
  }
});

// Emits 정의
const emit = defineEmits(['page-change']);

// 총 페이지 수 계산
const totalPages = computed(() => {
  return Math.ceil(props.totalItems / props.itemsPerPage);
});

// 페이지 변경 함수
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    emit('page-change', page);
  }
};
</script>

<style scoped>
/* 페이지네이션 스타일링 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  gap: 5px;
}

.pagination-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid #dee2e6;
  background-color: #fff;
  color: #495057;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-button.active {
  background-color: #90caf9;
  color: #fff;
  border-color: #64b5f6;
}

.pagination-button:hover:not(:disabled):not(.active) {
  background-color: #f8f9fa;
  border-color: #ced4da;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>