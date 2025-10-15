// import { defineConfig } from 'vite'
// import vue from '@vitejs/plugin-vue'

// // https://vite.dev/config/
// export default defineConfig({
//   plugins: [vue()],
// })



// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      // '/api/web' 경로로 시작하는 모든 요청을 백엔드 서버로 프록시합니다
      '/api/web': {
        target: 'http://orion.mokpo.ac.kr:8485',
        changeOrigin: true,
        // 필요한 경우 경로 재작성
        // rewrite: (path) => path.replace(/^\/api\/web/, '/api/web')
      }
    }
  }
})