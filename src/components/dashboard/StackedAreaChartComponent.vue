<template>
  <div class="stacked-area-chart-wrapper">
    <!-- 可选的上方表格 -->
    <div v-if="tableData && Object.keys(tableData).length > 0" class="table-header">
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="xValue in xAxisValues" :key="xValue" class="table-cell">
              {{ xValue }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td v-for="xValue in xAxisValues" 
                :key="xValue" 
                class="table-cell"
                :style="{ backgroundColor: getCellColor(tableData[xValue]) }">
              {{ tableData[xValue] || '' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 图表容器 -->
    <div class="chart-container" ref="chartContainer"></div>
    
    <!-- 加载中或错误覆盖层 -->
    <div v-if="loading" class="chart-overlay chart-loading">加载中...</div>
    <div v-else-if="error" class="chart-overlay chart-error">{{ error }}</div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import axios from 'axios';
import Plotly from 'plotly.js-dist';

export default defineComponent({
  name: 'StackedAreaChartComponent',
  props: {
    componentConfig: {
      type: Object,
      required: true
    }
  },
  setup(props, { expose }) {
    const chartContainer = ref(null);
    const loading = ref(true);
    const error = ref(null);
    const chartData = ref(null);
    const tableData = ref(null);
    const xAxisValues = ref([]);
    const resizeObserver = ref(null);

    // 防重复刷新逻辑
    let isRefreshing = false;
    let refreshTimer = null;
    const lastUpdateTime = ref(0);

    // 默认颜色配置
    const defaultColors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
      '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
    ];

    const loadChartData = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        console.log('开始加载堆叠面积图数据');
        
        // 构建URL，添加组件ID和时间戳
        let url = props.componentConfig.dataSource;
        if (url.includes('?')) {
          url += '&';
        } else {
          url += '?';
        }
        
        // 添加组件ID参数（如果存在）
        if (props.componentConfig.id) {
          url += `component_id=${props.componentConfig.id}&`;
        }
        
        // 添加时间戳防止缓存
        url += `_t=${Date.now()}`;
        
        const response = await axios.get(url);
        const data = response.data;
        
        console.log('收到的堆叠面积图数据:', data);
        
        // 解析数据格式
        if (data.stackedAreaData && data.stackedAreaData.data) {
          const stackedData = data.stackedAreaData;
          chartData.value = stackedData;
          
          // 从数据中提取 X 轴值（时间点）
          xAxisValues.value = Object.keys(stackedData.data).sort();
          
          // 从第一个数据点提取 key 顺序
          if (xAxisValues.value.length > 0) {
            const firstDataPoint = stackedData.data[xAxisValues.value[0]];
            chartData.value.keyOrder = Object.keys(firstDataPoint);
          } else {
            chartData.value.keyOrder = [];
          }
          
          // 处理表格数据（从顶级响应数据中获取）
          tableData.value = data.tableData || null;
          
          console.log('解析后的表格数据:', tableData.value);
          console.log('表格数据存在:', tableData.value !== null);
          console.log('表格数据键数量:', tableData.value ? Object.keys(tableData.value).length : 0);
          console.log('X轴值:', xAxisValues.value);
          
          loading.value = false;
          
          nextTick(() => {
            renderStackedAreaChart();
          });
        } else {
          throw new Error('数据格式不正确，需要包含 stackedAreaData.data 字段');
        }
      } catch (err) {
        error.value = `加载堆叠面积图数据失败: ${err.message}`;
        console.error('获取堆叠面积图数据出错:', err);
        loading.value = false;
      }
    };

    const renderStackedAreaChart = () => {
      console.log('开始渲染堆叠面积图');
      
      if (!chartContainer.value || !chartData.value) {
        console.warn('图表容器或数据为空，不执行渲染');
        return;
      }

      try {
        const { data, keyOrder, colors } = chartData.value;
        const xValues = xAxisValues.value;
        
        // 计算累积数据
        const cumulativeData = calculateCumulativeData(data, xValues, keyOrder);
        
        // 创建堆叠面积图的traces
        const traces = createStackedAreaTraces(cumulativeData, keyOrder, colors || defaultColors);
        
        // 布局配置
        const layout = {
          title: props.componentConfig.title || '堆叠面积图',
          autosize: true,
          margin: { l: 60, r: 30, t: 80, b: 60, pad: 4 },
          xaxis: {
            title: '时间/类别',
            autorange: true,
            fixedrange: false
          },
          yaxis: {
            title: '累积值',
            autorange: true,
            fixedrange: false
          },
          legend: {
            x: 1.02,
            y: 1,
            bgcolor: 'rgba(255,255,255,0.8)'
          },
          hovermode: 'x unified',
          showlegend: true
        };

        const config = {
          responsive: true,
          displayModeBar: true,
          modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
          displaylogo: false
        };

        Plotly.newPlot(chartContainer.value, traces, layout, config)
          .then(() => {
            return Plotly.relayout(chartContainer.value, {
              'xaxis.autorange': true,
              'yaxis.autorange': true,
              'autosize': true
            });
          })
          .then(() => {
            Plotly.Plots.resize(chartContainer.value);
          });
          
        console.log('堆叠面积图渲染完成');
      } catch (err) {
        console.error('堆叠面积图渲染失败:', err);
        error.value = `图表渲染失败: ${err.message}`;
      }
    };

    // 计算累积数据
    const calculateCumulativeData = (data, xValues, keyOrder) => {
      const cumulativeData = {};
      
      keyOrder.forEach(key => {
        cumulativeData[key] = [];
      });

      xValues.forEach((xValue, xIndex) => {
        const dataPoint = data[xValue] || {};
        let cumulativeSum = 0;
        
        keyOrder.forEach(key => {
          const currentValue = dataPoint[key] || 0;
          cumulativeSum += currentValue;
          cumulativeData[key].push({
            x: xValue,
            y: cumulativeSum,
            originalValue: currentValue
          });
        });
      });

      return cumulativeData;
    };

    // 创建堆叠面积图的traces
    const createStackedAreaTraces = (cumulativeData, keyOrder, colors) => {
      const traces = [];
      
      // 为每个key创建一个trace
      keyOrder.forEach((key, index) => {
        const points = cumulativeData[key];
        const xValues = points.map(p => p.x);
        const yValues = points.map(p => p.y);
        const originalValues = points.map(p => p.originalValue);
        
        // 创建填充区域的trace
        const areaTrace = {
          x: xValues,
          y: yValues,
          name: key,
          type: 'scatter',
          mode: 'lines',
          fill: index === 0 ? 'tozeroy' : 'tonexty', // 第一个填充到x轴，其他填充到上一个trace
          fillcolor: colors[index % colors.length] + '80', // 添加透明度
          line: {
            color: colors[index % colors.length],
            width: 2
          },
          hovertemplate: 
            `<b>${key}</b><br>` +
            `X: %{x}<br>` +
            `当前值: %{customdata}<br>` +
            `累积值: %{y}<br>` +
            '<extra></extra>',
          customdata: originalValues
        };
        
        traces.push(areaTrace);
      });

      return traces;
    };

    // 获取表格单元格颜色
    const getCellColor = (value) => {
      if (!value || !props.componentConfig.tableCellColors) {
        return 'transparent';
      }
      
      // 如果配置中有自定义颜色函数
      if (typeof props.componentConfig.tableCellColors === 'function') {
        return props.componentConfig.tableCellColors(value);
      }
      
      // 默认基于数值大小的颜色映射
      const numValue = parseFloat(value);
      if (isNaN(numValue)) return 'transparent';
      
      if (numValue > 0) {
        const intensity = Math.min(numValue / 100, 1); // 假设100为最大值
        return `rgba(76, 175, 80, ${intensity * 0.6})`; // 绿色渐变
      } else if (numValue < 0) {
        const intensity = Math.min(Math.abs(numValue) / 100, 1);
        return `rgba(244, 67, 54, ${intensity * 0.6})`; // 红色渐变
      }
      
      return 'transparent';
    };

    // 获取组件刷新延迟
    const getComponentDelay = () => {
      return props.componentConfig.id ? Math.min(100 * parseInt(props.componentConfig.id.toString().replace(/\D/g, '')), 2000) : 0;
    };

    // 统一的刷新处理方法
    const handleRefresh = (source, details = null, defaultDelay = 500) => {
      console.log(`🔔 [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 收到刷新请求，来源: ${source}`, details);
      
      // 清除之前的定时器
      if (refreshTimer) {
        clearTimeout(refreshTimer);
        refreshTimer = null;
      }
      
      // 计算延迟时间
      const delay = getComponentDelay() || defaultDelay;
      
      // 检查是否在短时间内重复刷新
      const now = Date.now();
      if (now - lastUpdateTime.value < 500) {
        console.log(`⏱️ [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 距离上次更新时间过短(${now - lastUpdateTime.value}ms)，跳过刷新`);
        return;
      }
      
      // 如果正在刷新中，跳过此次请求
      if (isRefreshing) {
        console.log(`⏱️ [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 正在刷新中，跳过重复请求`);
        return;
      }
      
      // 设置刷新定时器
      refreshTimer = setTimeout(() => {
        if (isRefreshing) return; // 双重检查
        
        isRefreshing = true;
        console.log(`⏱️ [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 开始刷新数据...`);
        
        refreshData().finally(() => {
          // 刷新完成后重置状态，允许下次刷新
          setTimeout(() => {
            isRefreshing = false;
          }, 1000); // 1秒内禁止重复刷新
        });
        
        refreshTimer = null;
      }, delay);
    };

    // 刷新数据方法（供外部调用）
    const refreshData = async () => {
      console.log(`🔄 [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 开始刷新数据...`);
      
      try {
        await loadChartData();
        console.log(`✅ [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 数据刷新完成`);
      } catch (err) {
        console.error(`❌ [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 数据刷新失败:`, err);
        throw err;
      } finally {
        lastUpdateTime.value = Date.now();
      }
    };

    // 监听仪表盘更新事件
    const handleDashboardUpdate = (event) => {
      const update = event.detail;
      
      // 过滤掉系统消息，避免不必要的刷新
      if (update && (update.type === 'connection_established' || update.type === 'heartbeat')) {
        console.log(`⏱️ [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 忽略系统消息:`, update.type);
        return;
      }
      
      // 检查是否需要刷新当前组件
      if (update && (
        update.componentId === props.componentConfig.id || 
        update.action === 'reload_config' ||
        update.action === 'force_refresh'
      )) {
        console.log(`⏱️ [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 将处理更新:`, update);
        handleRefresh('仪表盘更新', update, 200);
      } else {
        console.log(`⏱️ [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 跳过不相关更新:`, update);
      }
    };
    
    // 添加配置更新事件监听  
    const handleConfigUpdate = (event) => {
      const update = event.detail;
      
      // 只有在不是reload_config触发的配置更新时才刷新
      if (update && update.action !== 'reload_config') {
        handleRefresh('配置更新', update, 300);
      } else {
        console.log(`⏱️ [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 跳过reload_config触发的配置更新事件`);
      }
    };

    onMounted(() => {
      console.log('StackedAreaChartComponent 挂载完成');
      
      // 延迟初始化，避免重复请求
      const delay = getComponentDelay();
      setTimeout(() => {
        console.log(`⏰ [${new Date().toISOString()}] 堆叠面积图组件 ${props.componentConfig.id} 延迟 ${delay}ms 后开始初始化...`);
        loadChartData();
      }, delay);
      
      // 监听仪表盘事件
      window.addEventListener('dashboard-update', handleDashboardUpdate);
      window.addEventListener('dashboard-config-updated', handleConfigUpdate);
      
      // 添加窗口大小变化的响应式处理
      nextTick(() => {
        if (chartContainer.value) {
          resizeObserver.value = new ResizeObserver(() => {
            if (chartData.value && chartContainer.value) {
              console.log('检测到大小变化，重新调整堆叠面积图大小');
              Plotly.Plots.resize(chartContainer.value);
            }
          });
          resizeObserver.value.observe(chartContainer.value);
        }
      });
    });

    onUnmounted(() => {
      // 清理定时器
      if (refreshTimer) {
        clearTimeout(refreshTimer);
        refreshTimer = null;
      }
      
      // 清理事件监听器
      window.removeEventListener('dashboard-update', handleDashboardUpdate);
      window.removeEventListener('dashboard-config-updated', handleConfigUpdate);
      
      // 清理ResizeObserver
      if (resizeObserver.value) {
        resizeObserver.value.disconnect();
      }
    });

    // 监听配置变化，重新加载数据
    watch(() => props.componentConfig.dataSource, () => {
      loadChartData();
    });

    // 暴露方法给父组件
    expose({
      refreshData,
      fetchData: loadChartData
    });

    return {
      chartContainer,
      loading,
      error,
      tableData,
      xAxisValues,
      getCellColor,
      refreshData,
      handleRefresh,
      getComponentDelay
    };
  }
});
</script>

<style scoped>
.stacked-area-chart-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 400px;
  overflow: hidden;
}

.table-header {
  flex-shrink: 0;
  margin-bottom: 15px;
  max-height: 120px;
  overflow: auto;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f9f9f9;
  padding: 10px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  border: 1px solid #ccc;
  background-color: white;
  border-radius: 4px;
  overflow: hidden;
}

.data-table th,
.data-table td {
  border: 1px solid #ddd;
  text-align: center;
  min-width: 80px;
  padding: 8px 6px;
}

.data-table th {
  background-color: #4CAF50;
  color: white;
  font-weight: bold;
  font-size: 12px;
}

.table-cell {
  padding: 4px 6px;
  transition: background-color 0.2s;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-height: 300px;
}

.chart-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.chart-loading {
  color: #666;
  font-size: 16px;
}

.chart-error {
  color: #f44336;
  font-size: 14px;
  max-width: 300px;
  text-align: center;
}

/* 深度选择器控制 Plotly 生成的元素 */
:deep(.js-plotly-plot) {
  width: 100% !important;
  height: 100% !important;
  overflow: hidden !important;
}

:deep(.plot-container) {
  width: 100% !important;
  height: 100% !important;
}

:deep(.svg-container) {
  width: 100% !important;
  height: 100% !important;
}
</style>
