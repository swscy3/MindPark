<template>
  <v-card-text class="notification-filter">
    <v-row>
      <v-col cols="12" md="4">
        <v-text-field
          v-model="keyword"
          label="키워드 검색"
          prepend-inner-icon="mdi-magnify"
          clearable
          hide-details
          class="filter-input"
          @keyup.enter="search"
        ></v-text-field>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-row>
          <v-col cols="12" sm="6">
            <v-menu
              v-model="startDateMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              max-width="290px"
              min-width="auto"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="startDateFormatted"
                  label="시작 날짜"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  v-bind="props"
                  clearable
                  @click:clear="startDate = null"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="startDate"
                @update:model-value="startDateMenu = false"
              ></v-date-picker>
            </v-menu>
          </v-col>
          
          <v-col cols="12" sm="6">
            <v-menu
              v-model="endDateMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              max-width="290px"
              min-width="auto"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="endDateFormatted"
                  label="종료 날짜"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  v-bind="props"
                  clearable
                  @click:clear="endDate = null"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="endDate"
                @update:model-value="endDateMenu = false"
              ></v-date-picker>
            </v-menu>
          </v-col>
        </v-row>
      </v-col>
      
      <v-col cols="12" md="2" class="d-flex align-center justify-end">
        <v-btn
          color="primary"
          class="filter-button mr-2"
          @click="applyFilter"
        >
          필터 적용
        </v-btn>
        
        <v-btn
          text
          class="filter-reset-button"
          @click="resetFilter"
        >
          초기화
        </v-btn>
      </v-col>
    </v-row>
  </v-card-text>
</template>

<script>
export default {
  name: 'NotificationFilter',
  
  data() {
    return {
      keyword: '',
      startDate: null,
      endDate: null,
      startDateMenu: false,
      endDateMenu: false
    };
  },
  
  computed: {
    startDateFormatted() {
      return this.formatDate(this.startDate);
    },
    
    endDateFormatted() {
      return this.formatDate(this.endDate);
    }
  },
  
  methods: {
    formatDate(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      
      return `${year}-${month}-${day}`;
    },
    
    search() {
      this.$emit('search', this.keyword);
    },
    
    applyFilter() {
      this.$emit('filter', {
        keyword: this.keyword,
        startDate: this.startDate,
        endDate: this.endDate
      });
    },
    
    resetFilter() {
      this.keyword = '';
      this.startDate = null;
      this.endDate = null;
      this.$emit('reset');
    }
  }
};
</script>

<style src="../css/NotificationFilter.css"></style>