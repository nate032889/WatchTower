import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 8080,
    proxy: {
      '/api/v1': {
        target: 'http://api:8000',
        changeOrigin: true,
      },
      '/api/retrieval': {
        target: 'http://go-retrieval-service:8080',
        changeOrigin: true,
      }
    }
  }
})
