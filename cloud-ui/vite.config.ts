import path from 'path';

import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import svgLoader from 'vite-svg-loader';

export default defineConfig(() => ({
  plugins: [
    react(),
    svgLoader({
      svgo: false,
      defaultImport: 'raw',
    }),
  ],
  module: {
    rules: [
      {
        test: /\.symbol.svg$/,
        use: 'svg-inline-loader',
      },
    ],
  },
  resolve: {
    alias: {
      '#app': path.resolve(__dirname, './src/app'),
      '#assets': path.resolve(__dirname, './src/assets'),
      '#components': path.resolve(__dirname, './src/components'),
      '#constants': path.resolve(__dirname, './src/constants'),
      '#context': path.resolve(__dirname, './src/context'),
      '#hooks': path.resolve(__dirname, './src/hooks'),
      '#pages': path.resolve(__dirname, './src/pages'),
      '#services': path.resolve(__dirname, './src/services'),
      '#types': path.resolve(__dirname, './src/types'),
      '#utils': path.resolve(__dirname, './src/utils'),
      '#shared': path.resolve(__dirname, './src/shared'),
    },
  },
  css: {
    modules: {
      generateScopedName: '[name]__[local]___[hash:base64:5]',
    },
    preprocessorOptions: {
      scss: {},
    },
  },
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]',
      },
    },
  },
}));
