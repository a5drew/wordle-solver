import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Add this 'build' section to fix the 'import.meta' warning
  build: {
    target: 'esnext'
  }
})