/**
 * vite.config.js - Vite 빌드 도구 설정 파일
 * 개발 서버 포트, 프록시, 플러그인 등을 설정한다.
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],  // Vue 3 SFC 지원 플러그인
  server: {
    port: 5173,  // 개발 서버 포트
    proxy: {
      // /api 요청을 백엔드(FastAPI) 서버로 프록시 전달
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
