<template>
  <v-dialog
    v-model="dialogVisible"
    max-width="600px"
    @click:outside="closeDialog"
  >
    <v-card class="edit-modal">
      <v-card-title class="edit-modal-title">
        알림 로그 수정
        <v-spacer></v-spacer>
        <v-btn
          icon
          variant="text"
          @click="closeDialog"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text class="edit-modal-content">
        <div class="form-container">
          <v-text-field
            v-model="editedNotification.employeeId"
            label="사번"
            outlined
            dense
            readonly
            class="mb-4"
          ></v-text-field>
          
          <v-text-field
            v-model="editedNotification.name"
            label="이름"
            outlined
            dense
            readonly
            class="mb-4"
          ></v-text-field>
          
          <v-text-field
            v-model="editedNotification.symptom"
            label="증상"
            outlined
            dense
            readonly
            class="mb-4"
          ></v-text-field>
          
          <v-text-field
            v-model="editedNotification.risk"
            label="위험도"
            outlined
            dense
            readonly
            class="mb-4"
          ></v-text-field>
          
          <v-select
            v-model="editedNotification.editStatus"
            :items="editStatusOptions"
            label="처리상태"
            outlined
            dense
            class="mb-4"
          ></v-select>
          
          <v-textarea
            v-model="editedNotification.treatment"
            label="처치내용"
            outlined
            placeholder="응급상황에 대한 처치 내용을 입력하세요"
            class="mb-4"
          ></v-textarea>
          
          <div class="edit-history" v-if="editedNotification.updatedAt">
            <div class="edit-history-title">수정 이력</div>
            <div class="edit-history-item">
              <v-icon small class="mr-2">mdi-clock-outline</v-icon>
              최종 수정일: {{ formatDateTime(editedNotification.updatedAt) }}
            </div>
          </div>
        </div>
      </v-card-text>
      
      <v-divider></v-divider>
      
      <v-card-actions class="edit-modal-actions">
        <v-spacer></v-spacer>
        <v-btn
          text
          color="grey darken-1"
          @click="closeDialog"
        >
          취소
        </v-btn>
        <v-btn
          color="primary"
          @click="saveNotification"
        >
          저장
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'NotificationEditModal',
  
  props: {
    notification: {
      type: Object,
      default: () => ({})
    },
    show: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      dialogVisible: this.show,
      editedNotification: { 
        ...this.notification,
        treatment: this.notification.treatment || '',
        editStatus: this.notification.editStatus || '처리 중',
        risk: this.notification.risk || '주의'
      },
      editStatusOptions: ['처리 중', '처리 완료']
    };
  },
  
  watch: {
    show(newValue) {
      this.dialogVisible = newValue;
    },
    
    notification(newValue) {
      this.editedNotification = { 
        ...newValue,
        treatment: newValue.treatment || '',
        editStatus: newValue.editStatus || '처리 중',
        risk: newValue.risk || '주의'
      };
    }
  },
  
  methods: {
    closeDialog() {
      this.$emit('close');
    },
    
    saveNotification() {
      this.$emit('save', this.editedNotification);
    },
    
    formatDateTime(dateTime) {
      if (!dateTime) return '';
      
      const date = new Date(dateTime);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
  }
};
</script>

<style src="../css/NotificationEditModal.css"></style>