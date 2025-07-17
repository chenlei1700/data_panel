// API配置文件 - 管理不同仪表盘的后端服务配置
// 此文件由 auto-config-generator.py 自动生成，请勿手动编辑

export const API_CONFIG = {
  // 演示仪表盘 - 使用端口5004
  'demo_1': {
    baseURL: 'http://localhost:5004',
    name: '演示仪表盘数据服务',
    endpoints: {
      dashboardConfig: '/api/dashboard-config',
      chartData: '/api/chart-data',
      tableData: '/api/table-data',
      updates: '/api/dashboard/updates',
      health: '/health',
    }
  },

}

/**
 * 根据路由名称获取对应的API配置
 * @param {string} routeName - 路由名称
 * @returns {Object} API配置对象
 */
export const getApiConfig = (routeName) => {
  console.log(`🔍 查找路由 ${routeName} 的API配置...`);
  const config = API_CONFIG[routeName]
  if (!config) {
    console.warn(`❌ 未找到路由 ${routeName} 对应的API配置，使用默认配置`)
    return API_CONFIG['demo_1'] // 返回默认配置
  }
  console.log(`✅ 找到配置: ${config.name} (${config.baseURL})`)
  return config
}

/**
 * 获取所有可用的API服务列表
 * @returns {Array} 服务列表
 */
export const getAllServices = () => {
  return Object.keys(API_CONFIG).map(key => ({
    id: key,
    ...API_CONFIG[key]
  }))
}

/**
 * 检查服务健康状态
 * @param {string} serviceId - 服务ID
 * @returns {Promise<boolean>} 服务是否健康
 */
export const checkServiceHealth = async (serviceId) => {
  const config = API_CONFIG[serviceId]
  if (!config) return false
  
  try {
    const response = await fetch(`${config.baseURL}${config.endpoints.health}`, {
      method: 'GET',
      timeout: 3000
    })
    return response.ok
  } catch (error) {
    console.warn(`❌ 服务 ${serviceId} 健康检查失败:`, error)
    return false
  }
}

/**
 * 获取特定API端点的完整URL
 * @param {string} serviceName - 服务名称
 * @param {string} endpointName - 端点名称
 * @returns {string} 完整的API URL
 */
export const getApiEndpoint = (serviceName, endpointName) => {
  console.log(`🔍 获取 ${serviceName} 服务的 ${endpointName} 端点...`);
  const config = API_CONFIG[serviceName]
  if (!config) {
    console.warn(`❌ 未找到服务 ${serviceName} 的配置，使用默认配置`)
    const defaultConfig = API_CONFIG['demo_1']
    return `${defaultConfig.baseURL}${defaultConfig.endpoints[endpointName] || ''}`
  }
  const url = `${config.baseURL}${config.endpoints[endpointName] || ''}`
  console.log(`✅ 获取端点: ${url}`)
  return url
}

/**
 * 获取服务的基础URL
 * @param {string} serviceName - 服务名称
 * @returns {string} 基础URL
 */
export const getApiUrl = (serviceName) => {
  console.log(`🔍 获取 ${serviceName} 服务的基础URL...`);
  const config = API_CONFIG[serviceName]
  if (!config) {
    console.warn(`❌ 未找到服务 ${serviceName} 的配置，使用默认配置`)
    return API_CONFIG['demo_1'].baseURL
  }
  console.log(`✅ 基础URL: ${config.baseURL}`)
  return config.baseURL
}

/**
 * 获取服务信息
 * @param {string} serviceName - 服务名称
 * @returns {Object} 服务信息对象
 */
export const getServiceInfo = (serviceName) => {
  console.log(`🔍 获取 ${serviceName} 服务信息...`);
  const config = API_CONFIG[serviceName]
  if (!config) {
    console.warn(`❌ 未找到服务 ${serviceName} 的配置，返回默认服务信息`)
    const defaultConfig = API_CONFIG['demo_1']
    return {
      name: defaultConfig.name,
      baseURL: defaultConfig.baseURL,
      endpoints: defaultConfig.endpoints
    }
  }
  console.log(`✅ 服务信息: ${config.name}`)
  return {
    name: config.name,
    baseURL: config.baseURL,
    endpoints: config.endpoints
  }
}
