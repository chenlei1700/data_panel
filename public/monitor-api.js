// 添加网络请求监控脚本
// 在浏览器控制台中运行此脚本来监控API调用

console.log('🔍 开始监控API调用...');

// 保存原始的fetch函数
const originalFetch = window.fetch;

// 拦截所有fetch请求
window.fetch = function(...args) {
    const url = args[0];
    const options = args[1] || {};
    
    console.log('📡 API请求:', {
        url: url,
        method: options.method || 'GET',
        timestamp: new Date().toLocaleTimeString()
    });
    
    // 调用原始fetch并监控响应
    return originalFetch.apply(this, args)
        .then(response => {
            console.log('✅ API响应:', {
                url: url,
                status: response.status,
                statusText: response.statusText,
                timestamp: new Date().toLocaleTimeString()
            });
            return response;
        })
        .catch(error => {
            console.log('❌ API错误:', {
                url: url,
                error: error.message,
                timestamp: new Date().toLocaleTimeString()
            });
            throw error;
        });
};

// 添加路由信息检查
console.log('📍 当前路由信息:', {
    path: window.location.pathname,
    hash: window.location.hash,
    search: window.location.search
});

// 检查Vue Router信息(如果可用)
if (window.__VUE__ && window.__VUE__.$router) {
    console.log('🛣️ Vue Router信息:', {
        currentRoute: window.__VUE__.$router.currentRoute.value,
        meta: window.__VUE__.$router.currentRoute.value.meta
    });
}

console.log('监控已启动! 请执行一些操作来查看API调用...');
