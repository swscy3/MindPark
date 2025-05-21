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
        <v-form ref="form" v-model="valid">
          <v-text-field
            v-model="editedNotification.title"
            label="제목"
            outlined
            dense
            :rules="[v => !!v || '제목은 필수 입력 항목입니다.']"
            class="mb-4"
          ></v-text-field>
          
          <v-textarea
            v-model="editedNotification.content"
            label="내용"
            outlined
            :rules="[v => !!v || '내용은 필수 입력 항목입니다.']"
            class="mb-4"
          ></v-textarea>
          
          <v-select
            v-model="editedNotification.status"
            :items="statusOptions"
            label="상태"
            outlined
            dense
            class="mb-4"
          ></v-select>
          
          <v-textarea
            v-model="editedNotification.action"
            label="조치 내용"
            outlined
            placeholder="위급 상황에 대한 조치 내용을 입력하세요"
            class="mb-4"
          ></v-textarea>
          
          <div class="edit-history" v-if="editedNotification.updatedAt">
            <div class="edit-history-title">수정 이력</div>
            <div class="edit-history-item">
              <v-icon small class="mr-2">mdi-clock-outline</v-icon>
              최종 수정일: {{ formatDateTime(editedNotification.updatedAt) }}
            </div>
          </div>
        </v-form>
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
          :disabled="!valid"
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
      valid: true,
      editedNotification: { ...this.notification },
      statusOptions: ['처리 중', '완료', '보류']
    };
  },
  
  watch: {
    show(newValue) {
      this.dialogVisible = newValue;
    },
    
    notification(newValue) {
      this.editedNotification = { ...newValue };
    }
  },
  
  methods: {
    closeDialog() {
      this.$emit('close');
    },
    
    saveNotification() {
      if (this.$refs.form.validate()) {
        this.$emit('save', this.editedNotification);
      }
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