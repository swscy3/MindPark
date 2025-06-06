<template>
  <div class="search-section">
    <div class="search-box">
      <input 
        type="text" 
        :value="modelValue"
        :placeholder="placeholder"
        @input="handleInput"
        @keyup.enter="handleSearch"
      />
      <svg v-if="showIcon" xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <button @click="handleSearch">검색</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchBox',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: '검색어를 입력하세요'
    },
    showIcon: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:modelValue', 'search'],
  methods: {
    handleInput(event) {
      this.$emit('update:modelValue', event.target.value);
    },
    handleSearch() {
      this.$emit('search');
    }
  }
};
</script>

<style src="../css/SearchBox.css" scoped></style>