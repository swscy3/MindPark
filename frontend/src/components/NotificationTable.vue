<template>
  <v-card-text class="notification-table-container">
    <v-data-table
      :headers="headers"
      :items="notifications"
      :loading="loading"
      class="notification-table"
      :items-per-page="-1"
      hide-default-footer
    >
      <template v-slot:item.title="{ item }">
        <div class="title-cell">
          <v-badge
            v-if="item.isNew"
            color="error"
            dot
            inline
          ></v-badge>
          <span :class="{ 'new-notification': item.isNew }">{{ item.title }}</span>
        </div>
      </template>
      
      <template v-slot:item.createdAt="{ item }">
        {{ formatDateTime(item.createdAt) }}
      </template>
      
      <template v-slot:item.status="{ item }">
        <v-chip
          :color="getStatusColor(item.status)"
          text-color="white"
          size="small"
        >
          {{ item.status }}
        </v-chip>
      </template>
      
      <template v-slot:item.actions="{ item }">
        <v-btn
          icon
          variant="text"
          color="primary"
          @click="editNotification(item)"
        >
          <v-icon>mdi-pencil</v-icon>
        </v-btn>
      </template>
      
      <template v-slot:no-data>
        <div class="no-data">
          <v-icon large color="grey lighten-1">mdi-alert-circle-outline</v-icon>
          <p>알림 데이터가 없습니다.</p>
        </div>
      </template>
      
      <template v-slot:loading>
        <v-skeleton-loader
          v-for="n in 5"
          :key="n"
          type="list-item-two-line"
        ></v-skeleton-loader>
      </template>
    </v-data-table>
  </v-card-text>
</template>

<script>
export default {
  name: 'NotificationTable',
  
  props: {
    notifications: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      headers: [
        {
          title: '제목',
          key: 'title',
          width: '30%'
        },
        {
          title: '내용',
          key: 'content',
          width: '40%'
        },
        {
          title: '발생 시간',
          key: 'createdAt',
          width: '15%'
        },
        {
          title: '상태',
          key: 'status',
          width: '10%'
        },
        {
          title: '관리',
          key: 'actions',
          sortable: false,
          width: '5%'
        }
      ]
    };
  },
  
  methods: {
    formatDateTime(dateTime) {
      if (!dateTime) return '';
      
      const date = new Date(dateTime);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },
    
    getStatusColor(status) {
      switch (status) {
        case '처리 중':
          return 'warning';
        case '완료':
          return 'success';
        case '보류':
          return 'grey';
        default:
          return 'grey';
      }
    },
    
    editNotification(notification) {
      this.$emit('edit', notification);
    }
  }
};
</script>

<style src="../css/NotificationTable.css"></style>