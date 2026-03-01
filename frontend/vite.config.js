import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [vue()],
    server: {
      host: true,
      port: 8080,
      proxy: {
        // For local dev, proxy all /v1 requests to the Django backend
        '/v1': {
          target: env.VITE_API_V1_URL || 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
        // Proxy /intake requests to the Go backend
        '/intake': {
          target: env.VITE_API_INTAKE_URL || 'http://127.0.0.1:3000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/intake/, ''),
        }
      }
    }
  }
})
