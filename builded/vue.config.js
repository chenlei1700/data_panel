// vue.config.js
module.exports = {
  publicPath: '/',
  configureWebpack: {
    resolve: {
      alias: {
        '@': require('path').resolve(__dirname, 'src')
      },
      extensions: ['.js', '.vue', '.json']
    },
    entry: './src/main.js'
  },
  devServer: {
    port: 8081,
    proxy: {
      // 堆叠面积图演示API (端口5005)
      '/api/chart-data/stacked-area': {
        target: 'http://localhost:5005',
        changeOrigin: true,
        logLevel: 'debug'
      },
      
      // 主要API服务器 (演示服务器)
      '/api': {
        target: 'http://localhost:5004',
        changeOrigin: true,
        // 可以根据需要添加日志
        logLevel: 'debug'
      },
      
      // 多板块服务器 (如果需要特定API)
      '/api/multiplate': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        pathRewrite: {
          '^/api/multiplate': '/api'
        }
      },
      
      // 强势股服务器 (如果需要特定API)
      '/api/strong': {
        target: 'http://localhost:5002',
        changeOrigin: true,
        pathRewrite: {
          '^/api/strong': '/api'
        }
      }
    }
  }
}