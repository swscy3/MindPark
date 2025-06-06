<template>
  <v-container>
    <!-- 검색 기능 -->
    <v-row class="mb-5">
      <v-col cols="12" sm="6" md="4">
        <v-text-field
          v-model="search"
          label="검색"
          append-icon="mdi-magnify"
          hide-details
          class="search-field"
        ></v-text-field>
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <v-select
          v-model="searchType"
          :items="searchTypes"
          label="검색 조건"
          hide-details
          class="search-type"
        ></v-select>
      </v-col>
    </v-row>

    <!-- 공지사항 테이블 -->
    <v-data-table
      :headers="headers"
      :items="displayedItems"
      :search="search"
      :custom-filter="customFilter"
      class="notice-table"
      :items-per-page="10"
      :footer-props="{
        'items-per-page-options': [5, 10, 15, 20],
      }"
    >
      <!-- 일렬번호 -->
      <template v-slot:item.number="{ item }">
        <div class="number-cell">
          <v-icon 
            v-if="item.isPinned" 
            icon="mdi-pin" 
            color="pink-lighten-3" 
            class="mr-1 pin-icon"
          ></v-icon>
          {{ item.number }}
        </div>
      </template>

      <!-- 제목 -->
      <template v-slot:item.title="{ item }">
        <div 
          @click="openNotice(item)" 
          :class="{ 'read': item.isRead, 'title-cell': true }"
        >
          {{ item.title }}
        </div>
      </template>
    </v-data-table>

    <!-- 공지사항 상세 모달 -->
    <v-dialog v-model="dialog" max-width="600px">
      <v-card v-if="selectedNotice">
        <v-card-title class="dialog-title">
          {{ selectedNotice.title }}
        </v-card-title>
        <v-card-subtitle class="dialog-subtitle">
          {{ selectedNotice.author }} | {{ formatDate(selectedNotice.date) }}
        </v-card-subtitle>
        <v-divider></v-divider>
        <v-card-text class="dialog-content">
          {{ selectedNotice.content }}
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="dialog = false">닫기</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
export default {
  name: 'NoticeTable',
  data() {
    return {
      search: '',
      searchType: '제목',
      searchTypes: ['제목', '작성자'],
      headers: [
        { title: '번호', align: 'center', key: 'number', width: '80px' },
        { title: '제목', align: 'start', key: 'title' },
        { title: '작성자', align: 'center', key: 'author', width: '120px' },
        { title: '작성일', align: 'center', key: 'date', width: '120px' },
      ],
      notices: [
        { id: 1, number: 1, title: '[중요] 여름철 온열질환 예방 안내', author: '보건팀', date: '2023-06-25', content: '여름철 온열질환 예방 안내입니다.\n\n최근 폭염이 지속되면서 온열질환 발생 위험이 높아지고 있습니다. 다음 예방 수칙을 반드시 준수해주시기 바랍니다.\n\n1. 충분한 물 섭취하기 (갈증을 느끼지 않더라도 규칙적으로 물 마시기)\n2. 가장 더운 시간대(오후 12시~5시)에는 야외활동 자제하기\n3. 시원한 장소에서 휴식 취하기\n4. 헐렁하고 밝은 색상의 가벼운 옷 입기\n5. 야외 활동 시 챙이 넓은 모자 착용하기\n6. 직사광선 노출 시 자외선 차단제 바르기\n7. 알코올 섭취 자제하기\n\n온열질환 초기 증상(어지러움, 메스꺼움, 두통, 근육경련 등)이 나타나면 즉시 시원한 장소로 이동하여 휴식을 취하고, 증상이 심할 경우 즉시 의료기관을 방문하시기 바랍니다.\n\n건강한 여름 보내시기 바랍니다.', isPinned: true, isRead: false },
        { id: 2, number: 2, title: '신규 기능 출시 안내', author: '운영팀', date: '2023-02-15', content: '신규 기능 출시 안내입니다. 이번 업데이트에서는 사용자 편의성을 높이기 위한 다양한 기능이 추가되었습니다. 자세한 내용은 공지사항을 참고해 주세요.', isPinned: true, isRead: false },
        { id: 3, number: 3, title: '사용자 매뉴얼 업데이트', author: '개발팀', date: '2023-03-20', content: '사용자 매뉴얼이 업데이트 되었습니다. 변경된 내용은 홈페이지 하단의 매뉴얼 다운로드 섹션에서 확인하실 수 있습니다.', isPinned: true, isRead: false },
        { id: 4, number: 4, title: '정기 휴무 안내', author: '인사팀', date: '2023-04-05', content: '정기 휴무 안내입니다. 2023년 4월 30일부터 5월 5일까지 연휴로 인한 휴무가 있을 예정입니다. 긴급 문의는 비상연락망을 통해 가능합니다.', isPinned: false, isRead: false },
        { id: 5, number: 5, title: '서비스 이용약관 변경', author: '법무팀', date: '2023-04-10', content: '서비스 이용약관이 변경되었습니다. 주요 변경사항은 개인정보 처리 방식과 서비스 이용 조건에 관한 내용입니다. 자세한 내용은 이용약관 페이지를 참고해 주세요.', isPinned: false, isRead: false },
        { id: 6, number: 6, title: '개인정보 처리방침 개정', author: '보안팀', date: '2023-05-01', content: '개인정보 처리방침이 개정되었습니다. 이번 개정은 2023년 5월 15일부터 적용되며, 개인정보 보호를 강화하는 방향으로 변경되었습니다.', isPinned: false, isRead: false },
        { id: 7, number: 7, title: '서버 증설 완료 안내', author: '인프라팀', date: '2023-05-15', content: '서버 증설이 완료되었습니다. 이번 서버 증설로 서비스 안정성과 속도가 개선되었으며, 더 나은 서비스를 제공할 수 있게 되었습니다.', isPinned: false, isRead: false },
        { id: 8, number: 8, title: '연말 이벤트 안내', author: '마케팅팀', date: '2023-06-01', content: '연말 이벤트 안내입니다. 12월 한 달간 다양한 이벤트와 프로모션이 진행될 예정이니 많은 관심과 참여 부탁드립니다.', isPinned: false, isRead: false },
        { id: 9, number: 9, title: '모바일 앱 업데이트 안내', author: '개발팀', date: '2023-06-20', content: '모바일 앱이 업데이트 되었습니다. 버그 수정 및 성능 개선이 이루어졌으니 최신 버전으로 업데이트하여 이용해 주시기 바랍니다.', isPinned: false, isRead: false },
        { id: 10, number: 10, title: '하계 휴가 기간 공지', author: '인사팀', date: '2023-07-05', content: '하계 휴가 기간 공지입니다. 2023년 7월 25일부터 8월 5일까지는 하계 휴가 기간으로, 부서별 순환 휴가가 진행됩니다. 개인별 휴가 일정은 인사팀에서 별도 안내 예정입니다.', isPinned: false, isRead: false },
        { id: 11, number: 11, title: '주차장 이용 안내', author: '관리팀', date: '2023-07-10', content: '주차장 이용 안내입니다. 본사 주차장 공사로 인해 7월 15일부터 8월 15일까지 임시 주차장을 이용해 주시기 바랍니다. 임시 주차장 위치 및 셔틀버스 운행 시간은 첨부된 안내문을 참고해 주세요.', isPinned: false, isRead: false },
      ],
      dialog: false,
      selectedNotice: null
    }
  },
  computed: {
    displayedItems() {
      // 중요 공지사항을 상단에 표시하고 나머지는 최신순으로 정렬
      const pinnedNotices = this.notices
        .filter(notice => notice.isPinned)
        .sort((a, b) => new Date(b.date) - new Date(a.date));
      
      const regularNotices = this.notices
        .filter(notice => !notice.isPinned)
        .sort((a, b) => new Date(b.date) - new Date(a.date));
      
      return [...pinnedNotices, ...regularNotices];
    }
  },
  methods: {
    customFilter(value, search, item) {
      if (!search) return true;
      
      const searchLower = search.toString().toLowerCase();
      if (this.searchType === '제목') {
        return item.title.toLowerCase().includes(searchLower);
      } else if (this.searchType === '작성자') {
        return item.author.toLowerCase().includes(searchLower);
      }
      
      return false;
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    },
    openNotice(item) {
      this.selectedNotice = item;
      this.dialog = true;
      
      // 읽음 상태로 변경
      if (!item.isRead) {
        const index = this.notices.findIndex(notice => notice.id === item.id);
        if (index !== -1) {
          this.notices[index].isRead = true;
          // LocalStorage에 읽음 상태 저장
          this.saveReadStatus();
        }
      }
    },
    // LocalStorage에서 읽음 상태 불러오기
    loadReadStatus() {
      const savedReadStatus = localStorage.getItem('noticeReadStatus');
      if (savedReadStatus) {
        const readStatus = JSON.parse(savedReadStatus);
        
        // 저장된 읽음 상태를 notices 배열에 적용
        this.notices.forEach(notice => {
          if (readStatus.includes(notice.id)) {
            notice.isRead = true;
          }
        });
      }
    },
    // LocalStorage에 읽음 상태 저장
    saveReadStatus() {
      const readNoticeIds = this.notices
        .filter(notice => notice.isRead)
        .map(notice => notice.id);
      
      localStorage.setItem('noticeReadStatus', JSON.stringify(readNoticeIds));
    }
  },
  mounted() {
    // LocalStorage에서 읽음 상태 불러오기
    this.loadReadStatus();
  }
}
</script>

<style src="../css/Notice.css"></style>
