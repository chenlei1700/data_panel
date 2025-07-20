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
        const response = await axios.get(props.componentConfig.dataSource);
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

    // 刷新数据方法（供外部调用）
    const refreshData = () => {
      loadChartData();
    };

    // 监听仪表盘更新事件
    const handleDashboardUpdate = (event) => {
      const update = event.detail;
      if (update && update.componentId === props.componentConfig.id) {
        console.log('StackedAreaChart 接收到仪表盘更新:', update);
        refreshData();
      }
    };

    onMounted(() => {
      console.log('StackedAreaChartComponent 挂载完成');
      loadChartData();
      
      // 监听仪表盘更新事件
      window.addEventListener('dashboard-update', handleDashboardUpdate);
      
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
      window.removeEventListener('dashboard-update', handleDashboardUpdate);
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
      getCellColor
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
