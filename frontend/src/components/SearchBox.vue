<template>
  <div class="search-container">
    <input
      v-model="searchValue"
      :placeholder="placeholder"
      @input="handleInput"
      @keyup.enter="handleEnter"
      class="search-input"
    />
    <button 
      @click="handleSearch"
      class="search-button"
    >
      검색
    </button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

// Props 정의
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '검색어를 입력하세요'
  }
});

// Emits 정의
const emit = defineEmits(['update:modelValue', 'search']);

// 내부 상태
const searchValue = ref(props.modelValue);

// 입력 처리
const handleInput = () => {
  emit('update:modelValue', searchValue.value);
};

// 엔터키 처리
const handleEnter = () => {
  emit('search', searchValue.value);
};

// 검색 버튼 클릭 처리
const handleSearch = () => {
  emit('search', searchValue.value);
};

// 외부에서 modelValue 변경 시 동기화
watch(() => props.modelValue, (newValue) => {
  searchValue.value = newValue;
});
</script>

<style scoped>
/* 검색창 컨테이너 - 너비 확대 */
.search-container {
  position: relative;
  width: 600px; /* 400px → 600px로 확대 */
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.search-input {
  padding: 12px 16px !important;
  flex: 1 !important; /* 남은 공간 모두 차지 */
  background-color: #f8f9fa !important;
  border: 1px solid #e9ecef !important;
  border-radius: 4px !important;
  font-size: 14px !important;
  transition: all 0.2s ease !important;
  box-sizing: border-box !important;
  height: 44px !important;
}

.search-input:focus {
  outline: none !important;
  border-color: #90caf9 !important;
  box-shadow: 0 0 0 3px rgba(144, 202, 249, 0.3) !important;
}

/* 검색 버튼 스타일 */
.search-button {
  padding: 12px 20px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 44px;
  white-space: nowrap;
}

.search-button:hover {
  background-color: #1976d2;
}

.search-button:active {
  background-color: #1565c0;
}

/* Vuetify 스타일 충돌 방지 */
.search-container .v-input {
  margin: 0 !important;
  padding: 0 !important;
}

.search-container .v-input__control {
  min-height: auto !important;
}

.search-container .v-input__slot {
  margin: 0 !important;
  padding: 0 !important;
}

/* 반응형 디자인 추가 */
@media (max-width: 768px) {
  .search-container {
    width: 100%;
    max-width: 500px;
  }
}
</style>