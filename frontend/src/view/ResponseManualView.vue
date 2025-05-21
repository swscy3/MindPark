<template>
    <div class="response-manual-view">
      <div class="header">
        <h1>대응 메뉴얼 관리</h1>
        <p>응급 상황 대처 방안 및 안전 매뉴얼</p>
      </div>
  
      <div class="search-section">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="검색어를 입력하세요" 
            @keyup.enter="searchManuals"
          />
          <button @click="searchManuals">검색</button>
        </div>
      </div>
  
      <div class="category-filter">
        <button 
          v-for="category in categories" 
          :key="category.id"
          :class="{ active: selectedCategory === category.id }"
          @click="filterByCategory(category.id)"
        >
          {{ category.name }}
        </button>
      </div>
  
      <div class="manuals-grid">
        <div 
          v-for="manual in filteredManuals" 
          :key="manual.id" 
          class="manual-card"
          @click="openManualDetail(manual)"
        >
          <div class="card-image">
            <img :src="manual.imageUrl" :alt="manual.title" />
          </div>
          <div class="card-content">
            <h3>{{ manual.title }}</h3>
            <p>{{ manual.description }}</p>
            <div class="card-footer">
              <span class="category-tag">{{ getCategoryName(manual.category) }}</span>
              <span class="update-date">최종 업데이트: {{ formatDate(manual.updatedAt) }}</span>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 매뉴얼 상세 모달 -->
      <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
        <div class="modal-content detail-modal" @click.stop>
          <div class="modal-header">
            <h2>{{ selectedManual.title }}</h2>
            <button class="close-button" @click="closeDetailModal">×</button>
          </div>
          <div class="modal-body">
            <div class="manual-detail-content">
              <div class="manual-images">
                <img 
                  :src="selectedManual.imageUrl" 
                  :alt="selectedManual.title" 
                  class="main-image" 
                />
                <div class="additional-images" v-if="selectedManual.additionalImages && selectedManual.additionalImages.length">
                  <img 
                    v-for="(image, index) in selectedManual.additionalImages" 
                    :key="index"
                    :src="image.url" 
                    :alt="`${selectedManual.title} - 추가 이미지 ${index + 1}`"
                    @click="setMainImage(image.url)" 
                  />
                </div>
              </div>
              <div class="manual-text">
                <h3>설명</h3>
                <p>{{ selectedManual.description }}</p>
                
                <h3>대응 절차</h3>
                <ol>
                  <li v-for="(step, index) in selectedManual.steps" :key="index">
                    {{ step }}
                  </li>
                </ol>
                
                <h3>주의사항</h3>
                <ul>
                  <li v-for="(caution, index) in selectedManual.cautions" :key="index">
                    {{ caution }}
                  </li>
                </ul>
                
                <div class="additional-info" v-if="selectedManual.additionalInfo">
                  <h3>추가 정보</h3>
                  <p>{{ selectedManual.additionalInfo }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <!-- 버튼 제거 -->
          </div>
        </div>
      </div>
  
      <!-- 매뉴얼 등록/수정 모달 제거 -->
  
      <!-- 삭제 확인 모달 제거 -->
    </div>
  </template>
  
  <script>
  export default {
    name: 'ResponseManualView',
    data() {
      return {
        searchKeyword: '',
        selectedCategory: 'all',
        showDetailModal: false,
        selectedManual: null,
        
        categories: [
          { id: 'all', name: '전체' },
          { id: 'emergency', name: '응급 상황' },
          { id: 'safety', name: '안전 관리' },
          { id: 'medical', name: '의료 대응' },
          { id: 'disaster', name: '재난 대응' }
        ],
        
        manuals: [
          {
            id: 1,
            title: '온열질환 환자 대처방안',
            description: '폭염 시 발생할 수 있는 온열질환 환자의 증상 및 응급처치 방법에 대한 안내입니다.',
            category: 'medical',
            imageUrl: '/api/placeholder/600/400',
            additionalImages: [
              { url: '/api/placeholder/600/400' },
              { url: '/api/placeholder/600/400' }
            ],
            steps: [
              '환자를 시원한 장소로 이동시킵니다.',
              '옷을 느슨하게 하고 몸을 시원하게 합니다.',
              '의식이 있으면 차가운 물을 마시게 합니다.',
              '체온이 39도 이상이거나 의식이 없으면 즉시 119에 연락합니다.'
            ],
            cautions: [
              '의식이 없는 환자에게 물을 먹이지 마십시오.',
              '알코올이나 카페인이 함유된 음료는 피하십시오.',
              '체온이 급격히 내려가지 않도록 주의하십시오.'
            ],
            additionalInfo: '온열질환은 열사병, 열탈진, 열경련, 열부종 등으로 구분되며, 증상의 심각도에 따라 대처 방법이 달라질 수 있습니다.',
            createdAt: '2025-02-15',
            updatedAt: '2025-03-20'
          },
          {
            id: 2,
            title: '낙상 환자 대처방안',
            description: '낙상으로 인한 부상 환자 발생 시 응급처치 및 대응 방법에 대한 안내입니다.',
            category: 'emergency',
            imageUrl: '/api/placeholder/600/400',
            additionalImages: [
              { url: '/api/placeholder/600/400' }
            ],
            steps: [
              '환자의 의식과 호흡을 확인합니다.',
              '환자를 움직이지 말고 그대로 두십시오.',
              '출혈이 있으면 깨끗한 천으로 압박합니다.',
              '119에 신고하고 의료진의 지시를 기다립니다.'
            ],
            cautions: [
              '환자의 목이나 척추를 움직이지 마십시오.',
              '의식이 없는 환자는 회복 자세를 취하게 하십시오.',
              '머리 부상이 의심되면 즉시 전문적인 의료 도움을 요청하십시오.'
            ],
            additionalInfo: '',
            createdAt: '2025-01-10',
            updatedAt: '2025-02-28'
          },
          {
            id: 3,
            title: 'CPR 방법',
            description: '심폐소생술(CPR)의 올바른 시행 방법과 자동심장충격기(AED) 사용법에 대한 안내입니다.',
            category: 'emergency',
            imageUrl: '/api/placeholder/600/400',
            additionalImages: [
              { url: '/api/placeholder/600/400' },
              { url: '/api/placeholder/600/400' },
              { url: '/api/placeholder/600/400' }
            ],
            steps: [
              '반응과 호흡을 확인합니다.',
              '119에 신고하고 AED를 요청합니다.',
              '흉부 압박을 시작합니다: 깊이 5-6cm, 속도 분당 100-120회',
              '30회 흉부 압박 후 2회 인공호흡을 실시합니다.',
              'AED가 도착하면 지시에 따라 사용합니다.',
              '구조대가 도착할 때까지 계속합니다.'
            ],
            cautions: [
              '흉부 압박 중단 시간을 최소화하십시오.',
              '인공호흡이 불가능한 경우에도 흉부 압박만이라도 계속하십시오.',
              'AED 사용 시 환자의 몸에 물기가 없어야 합니다.'
            ],
            additionalInfo: 'CPR은 심정지 환자의 생존율을 높이는 중요한 응급처치입니다. 주기적인 교육과 훈련을 통해 정확한 방법을 익히는 것이 중요합니다.',
            createdAt: '2024-12-05',
            updatedAt: '2025-03-15'
          },
          {
            id: 4,
            title: '화재 발생 시 대피 요령',
            description: '화재 발생 시 신속하고 안전한 대피 방법과 화재 초기 대응에 대한 안내입니다.',
            category: 'disaster',
            imageUrl: '/api/placeholder/600/400',
            steps: [
              '화재 경보를 울리고 119에 신고합니다.',
              '엘리베이터를 이용하지 않고 계단으로 대피합니다.',
              '연기가 있는 경우 몸을 낮추고 젖은 수건으로 코와 입을 가립니다.',
              '출구가 막힌 경우 창문을 통해 구조를 요청합니다.'
            ],
            cautions: [
              '한 번 대피한 후에는 다시 건물 안으로 들어가지 마십시오.',
              '뜨거운 문손잡이를 만지지 마십시오.',
              '밀폐된 공간에서는 문틈을 옷이나 천으로 막아 연기가 들어오지 않도록 하십시오.'
            ],
            additionalInfo: '',
            createdAt: '2025-01-25',
            updatedAt: '2025-03-10'
          },
          {
            id: 5,
            title: '응급 지혈 방법',
            description: '심각한 출혈 발생 시 응급 지혈 방법과 쇼크 예방에 대한 안내입니다.',
            category: 'medical',
            imageUrl: '/api/placeholder/600/400',
            steps: [
              '깨끗한 천이나 거즈로 상처를 직접 압박합니다.',
              '가능하면 상처 부위를 심장보다 높게 유지합니다.',
              '지혈대는 마지막 수단으로만 사용합니다.',
              '119에 신고하고 전문적인 치료를 받습니다.'
            ],
            cautions: [
              '상처에서 이물질을 제거하지 마십시오.',
              '출혈이 심각할 경우 쇼크 증상에 주의하십시오.',
              '지혈대를 사용한 경우 적용 시간을 기록해 두십시오.'
            ],
            additionalInfo: '지혈은 생명을 구하는 중요한 응급처치입니다. 심각한 출혈이 있는 경우 최대한 빨리 전문적인 의료 도움을 받아야 합니다.',
            createdAt: '2025-02-08',
            updatedAt: '2025-03-05'
          }
        ],
        
        formData: {}
      };
    },
    computed: {
      filteredManuals() {
        let result = this.manuals;
        
        // 카테고리 필터링
        if (this.selectedCategory !== 'all') {
          result = result.filter(manual => manual.category === this.selectedCategory);
        }
        
        // 검색어 필터링
        if (this.searchKeyword) {
          const keyword = this.searchKeyword.toLowerCase();
          result = result.filter(manual => 
            manual.title.toLowerCase().includes(keyword) || 
            manual.description.toLowerCase().includes(keyword)
          );
        }
        
        return result;
      }
    },
    methods: {
      formatDate(dateString) {
        const date = new Date(dateString);
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      },
      
      getCategoryName(categoryId) {
        const category = this.categories.find(cat => cat.id === categoryId);
        return category ? category.name : '';
      },
      
      searchManuals() {
        // 검색은 computed에서 처리
        console.log('검색어로 필터링:', this.searchKeyword);
      },
      
      filterByCategory(categoryId) {
        this.selectedCategory = categoryId;
      },
      
      openManualDetail(manual) {
        this.selectedManual = { ...manual };
        this.showDetailModal = true;
      },
      
      closeDetailModal() {
        this.showDetailModal = false;
        this.selectedManual = null;
      },
      
      setMainImage(imageUrl) {
        if (this.selectedManual) {
          // 원본 이미지 URL 저장
          const originalMainImage = this.selectedManual.imageUrl;
          
          // 클릭한 이미지를 메인으로 설정
          this.selectedManual.imageUrl = imageUrl;
          
          // 추가 이미지 목록에서 찾아서 교체
          const additionalImageIndex = this.selectedManual.additionalImages.findIndex(img => img.url === imageUrl);
          if (additionalImageIndex !== -1) {
            this.selectedManual.additionalImages[additionalImageIndex].url = originalMainImage;
          }
        }
      }
    }
  };
  </script>

<style src="../css/ResponseManual.css"></style>