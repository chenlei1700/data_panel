// vue.config.js
module.exports = {
  publicPath: '/',
  devServer: {
    port: 8081,
    proxy: {
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