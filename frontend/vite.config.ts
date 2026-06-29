import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: process.env.VITE_APP_BASE_PATH ?? '/dify/',
  plugins: [react()],
  server: {
    proxy: {
      '/dify/api': {
        target: 'http://127.0.0.1:8000',
        rewrite: (path) => path.replace(/^\/dify\/api/, '/api'),
      },
      '/dify/uploads': {
        target: 'http://127.0.0.1:8000',
      },
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
