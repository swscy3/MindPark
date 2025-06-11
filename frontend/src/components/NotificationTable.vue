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
      <template v-slot:item.serialNumber="{ index }">
        {{ index + 1 }}
      </template>
      
      <template v-slot:item.symptom="{ item }">
        <div class="symptom-cell">
          <v-badge
            v-if="item.isNew"
            color="error"
            dot
            inline
          ></v-badge>
          <span :class="{ 'new-notification': item.isNew }">{{ item.symptom }}</span>
        </div>
      </template>
      
      <template v-slot:item.createdAt="{ item }">
        {{ formatDateTime(item.createdAt) }}
      </template>
      
      <template v-slot:item.updatedAt="{ item }">
        {{ item.updatedAt ? formatDateTime(item.updatedAt) : '-' }}
      </template>
      
      <template v-slot:item.editStatus="{ item }">
        <v-chip
          :color="getEditStatusColor(item.editStatus)"
          text-color="white"
          size="small"
        >
          {{ item.editStatus }}
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
          title: '일련번호',
          key: 'serialNumber',
          width: '8%',
          sortable: false
        },
        {
          title: '사번',
          key: 'employeeId',
          width: '10%'
        },
        {
          title: '이름',
          key: 'name',
          width: '10%'
        },
        {
          title: '증상',
          key: 'symptom',
          width: '20%'
        },
        {
          title: '발생시간',
          key: 'createdAt',
          width: '12%'
        },
        {
          title: '처치내용',
          key: 'treatment',
          width: '18%'
        },
        {
          title: '업데이트시간',
          key: 'updatedAt',
          width: '12%'
        },
        {
          title: '수정상태',
          key: 'editStatus',
          width: '12%'
        },
        {
          title: '수정버튼',
          key: 'actions',
          sortable: false,
          width: '8%'
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
    
    getEditStatusColor(editStatus) {
      switch (editStatus) {
        case '처리중':
        case '처치중':
          return 'warning';
        case '처리 완료':
        case '완료':
          return 'blue';
        default:
          return 'warning';
      }
    },
    
    editNotification(notification) {
      this.$emit('edit', notification);
    }
  }
};
</script>

<style src="../css/NotificationTable.css"></style>