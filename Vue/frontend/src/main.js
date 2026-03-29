/**
 * main.js - Vue 앱 진입점(Entry Point)
 * Vue 인스턴스를 생성하고 #app 요소에 마운트한다.
 */
import { createApp } from 'vue'
import './assets/style.css'  // 전역 스타일시트 임포트
import App from './App.vue'  // 루트 컴포넌트

// Vue 앱 생성 및 DOM에 마운트
createApp(App).mount('#app')
