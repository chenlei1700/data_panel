<template>
  <div class="table-component">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th 
              v-for="column in apiColumns" 
              :key="column.field"
              @click="sortBy(column.field)"
              :class="{ sortable: true, active: sortKey === column.field, asc: sortKey === column.field && sortOrder === 'asc', desc: sortKey === column.field && sortOrder === 'desc' }"
            >
              {{ column.header }}
              <span class="sort-icon" v-if="sortKey === column.field">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
          </tr>
        </thead>        <tbody>
          <tr v-for="(row, index) in sortedRows" :key="index">
            <td 
              v-for="column in apiColumns" 
              :key="column.field"
              :style="getCellBackgroundStyle(row, column.field)"
            >
              <!-- 股票名称列使用特殊渲染 -->
              <span v-if="column.field === 'stock_name'" v-html="renderStockLink(row[column.field], row['id'])"></span>
              <span v-else-if="column.field === '股票名称'" v-html="renderStockLink(row[column.field], row['股票ID'])"></span>
              <!-- 板块1-5列使用特殊渲染 -->
              <span v-else-if="['板块1', '板块2', '板块3', '板块4', '板块5', '板块名'].includes(column.field)" 
                    v-html="renderSectorNameCell({value: row[column.field], style: ''})"></span>
              <span v-else>{{ formatCellValue(row[column.field]) }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'TableComponent',  props: {
    componentConfig: {
      type: Object,
      required: true
    },
    backgroundColorConfig: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props, { expose }) {
    const apiData = ref({
      rows: [],
      columns: []
    });
    const loading = ref(true);
    const error = ref(null);
    
    // 排序相关状态
    const sortKey = ref('');
    const sortOrder = ref('asc'); // 'asc' 或 'desc'
    
    // 格式化单元格值
    const formatCellValue = (value) => {
      if (value === null || value === undefined) return '';
      
      // 如果是数字且需要格式化
      if (typeof value === 'number') {
        // 对于百分比类型，保留两位小数
        return Number.isInteger(value) ? value : value.toFixed(2);
      }
      
      return value;
    };
    
    // 渲染股票链接
    const renderStockLink = (stockName, stockId) => {
      if (!stockName || !stockId) return stockName || '';
      
      // 股票代码格式化为6位数字
      const paddedStockId = String(stockId).padStart(6, '0');
      
      // 返回带链接的HTML
      return `<a href="http://www.treeid/code_${paddedStockId}" onclick="changeCss(this, 'stockTableBody')" 
          style="color: blue; text-decoration: underline; cursor: pointer;">${stockName}</a>`;
    };
    
    const renderSectorNameCell = (cell) => {
      if (!cell || !cell.value) return '';
      
      // 提取括号前的部分
      const fullName = cell.value;
      // 当有多个括号时，取最后一个括号前的部分
      const parenIndex = fullName.lastIndexOf('(');
      
      // 如果有括号，只取括号前的部分，否则使用完整名称
      const sectorName = parenIndex !== -1 ? fullName.substring(0, parenIndex).trim() : fullName;
      
      // 创建带有点击事件的板块名链接
      return `<a href="#" 
        onclick="event.preventDefault(); window.updateSectorDashboard('${sectorName}'); return false;" 
        style="${cell.style || ''}; cursor: pointer; text-decoration: underline; color: blue;">
        ${fullName}
      </a>`;
    };
    
    // 排序方法
    const sortBy = (key) => {
      if (sortKey.value === key) {
        // 如果点击的是当前排序的列，切换排序顺序
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
      } else {
        // 设置新的排序列，默认升序
        sortKey.value = key;
        sortOrder.value = 'asc';
      }
    };
    
    // 获取API返回的列数据
    const apiColumns = computed(() => {
      return apiData.value.columns || [];
    });
    
    // 基于排序条件的计算属性
    const sortedRows = computed(() => {
      if (!sortKey.value) return apiData.value.rows || [];
      
      const sortedArray = [...(apiData.value.rows || [])];
      return sortedArray.sort((a, b) => {
        const valueA = a[sortKey.value];
        const valueB = b[sortKey.value];
        
        // 判断是否为数值类型
        const isNumeric = !isNaN(parseFloat(valueA)) && !isNaN(parseFloat(valueB));
        
        let comparison = 0;
        if (isNumeric) {
          // 数值比较
          comparison = parseFloat(valueA) - parseFloat(valueB);
        } else if (valueA instanceof Date && valueB instanceof Date) {
          // 日期比较
          comparison = valueA.getTime() - valueB.getTime();
        } else {
          // 字符串比较
          const stringA = String(valueA || '').toLowerCase();
          const stringB = String(valueB || '').toLowerCase();
          if (stringA < stringB) comparison = -1;
          if (stringA > stringB) comparison = 1;
        }
        
        // 根据排序顺序返回比较结果
        return sortOrder.value === 'asc' ? comparison : -comparison;
      });
    });
    
    // 判断是否是涨停数据表更新的更完善方式
    const isUpLimitTableUpdate = (update) => {
      // 检查组件ID是否匹配
      const isMatchingId =  update.componentId === 'upLimitTable';
                        
      // 多重条件判断
      return isMatchingId;
    };

    // 在处理更新事件时使用
    const handleDashboardUpdate = (event) => {
      const update = event.detail;
      if (isUpLimitTableUpdate(update)) {
        console.log('涨停数据表需要更新');
        refreshData();
      }
    };

    // 获取数据的方法
    const fetchData = async (url) => {
      loading.value = true;
      error.value = null;
      
      console.log('开始获取数据，URL:', url || props.componentConfig.dataSource);
      
      try {
        const response = await axios.get(url || props.componentConfig.dataSource);
        
        console.log('获取到的原始响应数据:', response);
        console.log('响应数据类型:', typeof response.data);
        console.log('响应数据结构:', response.data);
        
        // 处理返回的数据
        if (response.data) {
          // 检查是否有标准的rows和columns结构
          if (response.data.rows && response.data.columns) {
            console.log('数据使用标准的rows/columns格式');
            apiData.value = response.data;
          } 
          // 兼容其他格式
          else if (Array.isArray(response.data)) {
            console.log('数据是纯数组格式，转换为标准格式');
            apiData.value = {
              rows: response.data,
              columns: response.data.length > 0 ? 
                Object.keys(response.data[0]).map(key => ({
                  field: key,
                  header: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')
                })) : []
            };
          } 
          else if (response.data.data && Array.isArray(response.data.data)) {
            console.log('数据使用 { data: [...] } 格式，转换为标准格式');
            apiData.value = {
              rows: response.data.data,
              columns: response.data.columns || (response.data.data.length > 0 ? 
                Object.keys(response.data.data[0]).map(key => ({
                  field: key,
                  header: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')
                })) : [])
            };
          } 
          else {
            console.log('无法识别的数据格式');
            apiData.value = { rows: [], columns: [] };
            error.value = '无法识别返回的数据格式';
          }
          
          console.log('处理后的表格数据:', apiData.value);
        } else {
          console.log('响应数据为空');
          apiData.value = { rows: [], columns: [] };
          error.value = '返回数据为空';
        }
      } catch (err) {
        console.error('获取表格数据失败:', err);
        error.value = '加载数据失败: ' + (err.message || '未知错误');
        apiData.value = { rows: [], columns: [] };
      } finally {
        loading.value = false;
        
        // 最终状态日志
        console.log('数据加载完成，状态:', {
          hasError: !!error.value, 
          errorMessage: error.value,
          rowsLength: (apiData.value.rows && apiData.value.rows.length) || 0,
          columnsLength: (apiData.value.columns && apiData.value.columns.length) || 0
        });
      }
    };
    
    const updateDashboard = async (sector) => {
      try {
        // 向Flask服务器发送更新请求
        const response = await fetch('http://localhost:5001/api/dashboard/update', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            componentId: 'chart2',  // 要更新的组件ID
            params: { sectors: sector }  // 新的板块名称
          })
        });
        
        const result = await response.json();
        console.log('更新请求已发送:', result);
        
        response = await fetch('http://localhost:5002/api/dashboard/update', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            componentId: 'chart2',  // 要更新的组件ID
            params: { sectors: sector }  // 新的板块名称
          })
        });
        
        result = await response2.json();
        console.log('更新请求已发送:', result);
        
        
      } catch (error) {
        console.error('发送更新请求失败:', error);
      }
    };

    // 监听组件配置变化
    watch(() => props.componentConfig.dataSource, (newVal) => {
      if (newVal) {
        fetchData(newVal);
      }
    });
    
    const refreshData = () => {
      console.log('正在刷新表格数据...');
      fetchData(props.componentConfig.dataSource);
    };
    
    onMounted(() => {
      fetchData();
      
      // 定义全局函数
      window.updateSectorDashboard = (sector) => {
        if (sector) {
          updateDashboard(sector);
          console.log(`正在更新${sector}板块图表...`);
        }
      };
      
      // 添加事件监听
      const handleDashboardUpdate = (event) => {
        const update = event.detail;
        console.log('接收到仪表盘更新事件:', update);
        
        // 检查是否是涨停数据表更新
        if (update && update.componentId === props.componentConfig.id) {
          refreshData();
        }
      };
      
      window.addEventListener('dashboard-update', handleDashboardUpdate);
      
      // 清理函数
      return () => {
        window.removeEventListener('dashboard-update', handleDashboardUpdate);
      };
    });
    
    // 暴露方法给父组件
    expose({
      fetchData,
      refreshData
    });
    
    return {
      apiData,
      apiColumns,
      loading,
      error,
      sortKey,
      sortOrder,
      sortBy,
      sortedRows,
      formatCellValue,
      renderStockLink,
      renderSectorNameCell
    };
  }
});
</script>

<style scoped>
/* 保持原有样式 */
.table-component {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.loading, .error {
  padding: 20px;
  text-align: center;
}

.error {
  color: #f44336;
}

.table-wrapper {
  flex: 1;
  overflow: auto;
  min-height: 0px;  /* 设置最小高度 */
  display: flex;
  flex-direction: column;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  flex: 1; /* 让表格占据所有可用空间 */
}

.data-table th, .data-table td {
  padding: 10px 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.data-table th {
  font-weight: 600;
  background-color: #f5f5f5;
  position: sticky;
  top: 0;
  z-index: 1;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
  position: relative;
  padding-right: 25px; /* 为排序图标留出空间 */
}

.data-table th.sortable:hover {
  background-color: #e9e9e9;
}

.data-table th.active {
  background-color: #eef5ff;
}

.sort-icon {
  position: absolute;
  right: 8px;
  color: #606060;
}

.data-table th.asc .sort-icon {
  color: #1976d2;
}

.data-table th.desc .sort-icon {
  color: #1976d2;
}

/* 表格行的悬停效果 */
.data-table tbody tr:hover {
  background-color: #f5f9ff;
}

/* 斑马纹效果 */
.data-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

/* 允许v-html内容中的链接样式生效 */
:deep(.stock-link) {
  color: #1976d2;
  text-decoration: underline;
  cursor: pointer;
}

:deep(.stock-link:hover) {
  color: #0d47a1;
}
</style>