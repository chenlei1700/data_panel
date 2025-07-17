// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

const app = createApp(App)
app.use(router)
app.use(store)  // 确保这行代码正确
app.mount('#app')