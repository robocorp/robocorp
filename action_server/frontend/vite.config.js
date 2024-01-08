/* eslint-disable import/no-extraneous-dependencies */
import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';
import path from 'path';
import react from '@vitejs/plugin-react';

export default defineConfig({
  server: {
    port: 8085,
    proxy: {
      '/api': 'http://localhost:8080',
      '/openapi.json': 'http://localhost:8080',
      '/config': 'http://localhost:8080',
      '/api/ws': {
        target: 'ws://localhost:8080',
        ws: true,
      },
    },
  },
  resolve: {
    alias: {
      '~': path.join(__dirname, 'src'),
    },
  },
  plugins: [react(), viteSingleFile()],
});
