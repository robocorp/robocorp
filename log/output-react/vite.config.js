/* eslint-disable import/no-extraneous-dependencies */
import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';
import path from 'path';
import react from '@vitejs/plugin-react';

export default defineConfig({
  server: {
    port: 8080,
  },
  resolve: {
    alias: {
      '~': path.join(__dirname, 'src'),
    },
  },
  plugins: [react(), viteSingleFile()],
});
