<template>
  <div class="notification-log-container">
    <v-card class="notification-log-card">
      <v-card-title class="notification-log-title">
        알림 로그 조회
      </v-card-title>
      
      <NotificationFilter 
        @search="handleSearch" 
        @filter="handleFilter"
        @reset="resetFilters"
      />
      
      <NotificationTable 
        :notifications="filteredNotifications" 
        :loading="loading"
        @edit="openEditModal"
      />
      
      <NotificationEditModal 
        v-if="selectedNotification"
        :notification="selectedNotification"
        :show="showEditModal"
        @close="closeEditModal"
        @save="saveNotification"
      />
    </v-card>
  </div>
</template>

<script>
import NotificationFilter from '../components/NotificationFilter.vue';
import NotificationTable from '../components/NotificationTable.vue';
import NotificationEditModal from '../components/NotificationEditModal.vue';

export default {
  name: 'NotificationLogView',
  
  components: {
    NotificationFilter,
    NotificationTable,
    NotificationEditModal
  },
  
  data() {
    return {
      notifications: [],
      filteredNotifications: [],
      loading: false,
      filters: {
        keyword: '',
        startDate: null,
        endDate: null
      },
      selectedNotification: null,
      showEditModal: false
    };
  },
  
  methods: {
    async fetchNotifications() {
      this.loading = true;
      try {
        // 임시 데이터
        setTimeout(() => {
          this.notifications = Array.from({ length: 20 }, (_, i) => ({
            id: i + 1,
            employeeId: `EMP${String(i + 1).padStart(3, '0')}`,
            name: `직원${i + 1}`,
            symptom: `증상 ${i + 1}`,
            treatment: `처치내용 ${i + 1}`,
            createdAt: new Date(Date.now() - i * 86400000).toISOString(),
            updatedAt: i < 10 ? new Date(Date.now() - i * 43200000).toISOString() : null,
            isNew: i < 5,
            editStatus: i < 15 ? '처치중' : '처치 완료'
          }));
          
          // 최신순 정렬 (오래된 것이 뒤로)
          this.notifications.sort((a, b) => 
            new Date(b.createdAt) - new Date(a.createdAt)
          );
          
          this.filteredNotifications = [...this.notifications];
          this.loading = false;
        }, 1000);
      } catch (error) {
        console.error('Failed to fetch notifications:', error);
        this.loading = false;
      }
    },
    
    handleSearch(keyword) {
      this.filters.keyword = keyword;
      this.applyFilters();
    },
    
    handleFilter(filters) {
      this.filters = { ...filters };
      this.applyFilters();
    },
    
    resetFilters() {
      this.filters = {
        keyword: '',
        startDate: null,
        endDate: null
      };
      this.filteredNotifications = [...this.notifications];
    },
    
    applyFilters() {
      let result = [...this.notifications];
      
      // 키워드 필터
      if (this.filters.keyword) {
        const keyword = this.filters.keyword.toLowerCase();
        result = result.filter(item => 
          item.employeeId.toLowerCase().includes(keyword) ||
          item.name.toLowerCase().includes(keyword) ||
          item.symptom.toLowerCase().includes(keyword) || 
          item.treatment.toLowerCase().includes(keyword)
        );
      }
      
      // 날짜 필터
      if (this.filters.startDate) {
        const startDate = new Date(this.filters.startDate);
        result = result.filter(item => 
          new Date(item.createdAt) >= startDate
        );
      }
      
      if (this.filters.endDate) {
        const endDate = new Date(this.filters.endDate);
        endDate.setHours(23, 59, 59);
        result = result.filter(item => 
          new Date(item.createdAt) <= endDate
        );
      }
      
      this.filteredNotifications = result;
    },
    
    openEditModal(notification) {
      this.selectedNotification = { ...notification };
      this.showEditModal = true;
    },
    
    closeEditModal() {
      this.showEditModal = false;
      this.selectedNotification = null;
    },
    
    saveNotification(updatedNotification) {
      // 임시로 로컬 데이터 업데이트
      const index = this.notifications.findIndex(n => n.id === updatedNotification.id);
      if (index !== -1) {
        this.notifications[index] = { 
          ...updatedNotification,
          updatedAt: new Date().toISOString()
        };
        
        // 필터링된 목록도 업데이트
        const filteredIndex = this.filteredNotifications.findIndex(n => n.id === updatedNotification.id);
        if (filteredIndex !== -1) {
          this.filteredNotifications[filteredIndex] = { 
            ...updatedNotification,
            updatedAt: new Date().toISOString()
          };
        }
      }
      
      this.closeEditModal();
    }
  },
  
  created() {
    this.fetchNotifications();
  }
};
</script>

<style src="../css/NotificationLog.css"></style>