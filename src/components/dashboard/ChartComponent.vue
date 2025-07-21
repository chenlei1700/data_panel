<template>
<div class="chart-wrapper">
    <!-- 图表容器始终存在 -->
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
    name: 'ChartComponent',
    props: {
      componentConfig: {
        type: Object,
        required: true
      }
    },
    setup(props) {
      const chartContainer = ref(null);
      const loading = ref(true);
      const error = ref(null);
      const chartData = ref(null);
      
      const resizeObserver = ref(null);
      
      // 防止重复刷新的控制变量
      let isRefreshing = false;
      let refreshTimer = null;
      
      // 事件处理函数引用，用于清理
      let handleDashboardUpdate = null;
      let handleConfigUpdate = null;
      
      // 获取组件刷新延迟
      const getComponentDelay = () => {
        return props.componentConfig.id ? Math.min(100 * parseInt(props.componentConfig.id.toString().replace(/\D/g, '')), 2000) : 0;
      };
      
      // 刷新数据方法
      const refreshData = () => {
        console.log(`⏱️ [${new Date().toISOString()}] 组件 ${props.componentConfig.id} 正在刷新图表数据...`);
        console.log(`⏱️ [${new Date().toISOString()}] 当前数据源:`, props.componentConfig.dataSource);
        
        // 在数据源URL中添加时间戳防止缓存
        const currentDataSource = props.componentConfig.dataSource;
        if (currentDataSource) {
          const url = new URL(currentDataSource);
          url.searchParams.set('_refresh', Date.now().toString());
          console.log(`⏱️ [${new Date().toISOString()}] 添加刷新参数后的数据源:`, url.toString());
          return loadChartData(url.toString());
        } else {
          return loadChartData();
        }
      };
      
      // 统一的刷新处理函数，避免重复刷新
      const handleRefresh = (eventType, update, delay = 200) => {
        console.log(`⏱️ [${new Date().toISOString()}] 图表组件 ${props.componentConfig.id} 接收到${eventType}事件:`, update);
        
        // 如果正在刷新，清除之前的定时器
        if (refreshTimer) {
          clearTimeout(refreshTimer);
          refreshTimer = null;
        }
        
        // 如果正在刷新中，跳过此次请求
        if (isRefreshing) {
          console.log(`⏱️ [${new Date().toISOString()}] 图表组件 ${props.componentConfig.id} 正在刷新中，跳过重复请求`);
          return;
        }
        
        // 设置刷新定时器
        refreshTimer = setTimeout(() => {
          if (isRefreshing) return; // 双重检查
          
          isRefreshing = true;
          console.log(`⏱️ [${new Date().toISOString()}] 图表组件 ${props.componentConfig.id} 开始刷新数据...`);
          
          refreshData().finally(() => {
            // 刷新完成后重置状态，允许下次刷新
            setTimeout(() => {
              isRefreshing = false;
            }, 1000); // 1秒内禁止重复刷新
          });
          
          refreshTimer = null;
        }, delay);
      };
      
      // 创建事件处理函数
      const createEventHandlers = () => {
        // 仪表盘更新事件监听
        handleDashboardUpdate = (event) => {
          const update = event.detail;
          
          // 过滤掉系统消息，避免不必要的刷新
          if (update && (update.type === 'connection_established' || update.type === 'heartbeat')) {
            console.log(`⏱️ [${new Date().toISOString()}] 图表组件 ${props.componentConfig.id} 忽略系统消息:`, update.type);
            return;
          }
          
          // 检查是否需要刷新当前组件
          if (update && (
            update.componentId === props.componentConfig.id || 
            update.action === 'reload_config' ||
            update.action === 'force_refresh'
          )) {
            console.log(`⏱️ [${new Date().toISOString()}] 图表组件 ${props.componentConfig.id} 将处理更新:`, update);
            handleRefresh('仪表盘更新', update, 200);
          } else {
            console.log(`⏱️ [${new Date().toISOString()}] 图表组件 ${props.componentConfig.id} 跳过不相关更新:`, update);
          }
        };
        
        // 配置更新事件监听  
        handleConfigUpdate = (event) => {
          const update = event.detail;
          
          // 只有在不是reload_config触发的配置更新时才刷新
          if (update && update.action !== 'reload_config') {
            handleRefresh('配置更新', update, 300);
          } else {
            console.log(`⏱️ [${new Date().toISOString()}] 图表组件 ${props.componentConfig.id} 跳过reload_config触发的配置更新事件`);
          }
        };
      };
      
      const loadChartData = async (url) => {
        loading.value = true;
        error.value = null;
        
        const targetUrl = url || props.componentConfig.dataSource;
        console.log('开始加载图表数据，URL:', targetUrl);
        
        try {
          // 构建带有componentId参数的URL
          const urlObj = new URL(targetUrl);
          
          // 添加componentId参数
          if (props.componentConfig.id) {
            urlObj.searchParams.set('componentId', props.componentConfig.id);
            console.log('添加componentId参数:', props.componentConfig.id);
          }
          
          const finalUrl = urlObj.toString();
          console.log('最终请求URL:', finalUrl);
          
          const response = await axios.get(finalUrl);
          chartData.value = response.data;
          console.log('收到的图表数据:', chartData.value);
          
          // 先将 loading 设为 false，让容器渲染出来
          loading.value = false;
          
          // 使用 nextTick 确保 DOM 已更新后再渲染图表
          nextTick(() => {
            console.log('nextTick 后检查容器:', chartContainer.value);
            renderChart();
          });
        } catch (err) {
          error.value = `加载图表数据失败: ${err.message}`;
          console.error('获取图表数据出错:', err);
          loading.value = false;
        }
      };
      
      const renderChart = () => {
        console.log('renderChart()开始执行');
        console.log('chartContainer.value:', chartContainer.value);
        console.log('chartData.value:', chartData.value);
        
        if (!chartContainer.value || !chartData.value) {
          console.warn('图表容器或数据为空，不执行渲染');
          return;
        }
        
        console.log('开始渲染图表', chartContainer.value, chartData.value);
        
        // 判断数据格式：Plotly标准格式 vs 简化格式
        let traces;
        let layoutConfig = {};
        
        if (chartData.value.data && Array.isArray(chartData.value.data)) {
          // Plotly标准格式：{ chartType, data: [...], layout }
          const { chartType, data, layout } = chartData.value;
          layoutConfig = layout || {};
          traces = data;  // 直接使用data数组作为traces，因为它们已经是Plotly格式
          
          // 对于不完整的traces，添加必要的属性
          traces = traces.map(trace => {
            const completeTrace = { ...trace };
            
            // 确保每个trace都有type属性
            if (!completeTrace.type && chartType) {
              completeTrace.type = chartType;
            }
            
            // 为散点图/折线图添加默认mode
            if ((completeTrace.type === 'scatter' || !completeTrace.type) && !completeTrace.mode) {
              completeTrace.mode = 'lines+markers';
            }
            
            return completeTrace;
          });
        } else {
          // 新格式：直接的图表数据对象
          traces = [{
            x: chartData.value.x,
            y: chartData.value.y,
            name: chartData.value.name || '数据系列',
            type: chartData.value.type || 'scatter',
            mode: chartData.value.mode || 'lines'
          }];
          
          // 添加其他可能的图表属性
          if (chartData.value.marker) traces[0].marker = chartData.value.marker;
          if (chartData.value.line) traces[0].line = chartData.value.line;
        }
        
        console.log('准备渲染的 traces:', traces);
        
        // 排序数据 - 按最后一个点的值从高到低
        if (traces.length > 1) {
          traces.sort((a, b) => {
            const lastAY = a.y && a.y.length > 0 ? a.y[a.y.length - 1] : 0;
            const lastBY = b.y && b.y.length > 0 ? b.y[b.y.length - 1] : 0; 
            return lastBY - lastAY;
          });
        }
        
        // 默认布局 + 自定义布局
        const plotlyLayout = {
            autosize: true,
            // 设置合适的边距确保内容完整显示
            margin: { 
                l: 60,   // 左边距，为y轴标签留空间
                r: 30,   // 右边距
                t: 50,   // 顶部边距，为标题留空间
                b: 60,   // 底部边距，为x轴标签留空间
                pad: 4
            },
            // 动态设置宽高以适应容器
            width: chartContainer.value.clientWidth,
            height: chartContainer.value.clientHeight || 400,
            // 确保坐标轴能自动调整范围显示所有数据
            yaxis: {
                ...layoutConfig.yaxis,
                autorange: true,     // 自动调整y轴范围显示所有数据
                fixedrange: false    // 允许缩放以便查看细节
            },
            xaxis: {
                ...layoutConfig.xaxis,
                autorange: true,     // 自动调整x轴范围显示所有数据
                fixedrange: false    // 允许缩放以便查看细节
            },
            // 图例设置，避免被裁剪
            legend: {
                orientation: "h",    // 水平排列图例
                x: 0,
                y: -0.15,           // 放在图表下方
                xanchor: 'left',
                yanchor: 'top'
            },
            ...layoutConfig
            };
          // 响应式配置
        const config = {
            responsive: true,        // 启用响应式
            displayModeBar: 'hover', // 只在悬停时显示工具栏
            displaylogo: false,
            modeBarButtonsToRemove: ['select2d', 'lasso2d'],  // 保留自动缩放功能
            scrollZoom: true,        // 允许滚轮缩放
            doubleClick: 'autosize', // 双击自适应大小
            staticPlot: false        // 保持交互功能
            };            try {
                // 渲染图表
                Plotly.newPlot(chartContainer.value, traces, plotlyLayout, config)
                .then(() => {
                    // 自动调整以确保内容完全可见
                    return Plotly.relayout(chartContainer.value, {
                        'xaxis.autorange': true,
                        'yaxis.autorange': true,
                        'autosize': true
                    });
                })
                .then(() => {
                    // 确保图表适应容器大小
                    Plotly.Plots.resize(chartContainer.value);
                });
                console.log('图表渲染完成');
                } catch (err) {
                console.error('图表渲染失败:', err);
                }
      };
      
      onMounted(() => {
        console.log('ChartComponent 挂载完成, chartContainer:', chartContainer.value);
        
        const componentDelay = getComponentDelay();
        console.log(`⏱️ [${new Date().toISOString()}] 图表组件 ${props.componentConfig.id} 将在 ${componentDelay}ms 后开始加载数据`);
        
        setTimeout(() => {
          loadChartData();
        }, componentDelay);
        
        // 创建并注册事件处理函数
        createEventHandlers();
        window.addEventListener('dashboard-update', handleDashboardUpdate);
        window.addEventListener('dashboard-config-updated', handleConfigUpdate);
        
        // 添加窗口大小变化的响应式处理
        nextTick(() => {
          if (chartContainer.value) {
            resizeObserver.value = new ResizeObserver(() => {
              if (chartData.value && chartContainer.value) {
                console.log('检测到大小变化，重新调整图表大小');
                Plotly.Plots.resize(chartContainer.value);
              }
            });
            resizeObserver.value.observe(chartContainer.value);
          }
        });

        // 添加调试日志
        setTimeout(() => {
            if (chartContainer.value) {
            console.log('容器尺寸:', {
                clientWidth: chartContainer.value.clientWidth,
                clientHeight: chartContainer.value.clientHeight,
                offsetWidth: chartContainer.value.offsetWidth,
                offsetHeight: chartContainer.value.offsetHeight,
                scrollWidth: chartContainer.value.scrollWidth,
                scrollHeight: chartContainer.value.scrollHeight
            });
            
            // 检查 Plotly 生成的元素
            const plotElement = chartContainer.value.querySelector('.js-plotly-plot');
            if (plotElement) {
                console.log('Plotly元素尺寸:', {
                clientWidth: plotElement.clientWidth,
                clientHeight: plotElement.clientHeight,
                scrollWidth: plotElement.scrollWidth,
                scrollHeight: plotElement.scrollHeight
                });
            }
            }
        }, 1000);
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
      
      return {
        chartContainer,
        loading,
        error,
        refreshData,
        handleRefresh,
        getComponentDelay
      };
    }
  });
</script>
  
<style scoped>
.chart-wrapper {
    display: grid;
    grid-template-areas: "chart";
    width: 100%;
    height: 100%;      /* 使用100%高度而不是固定高度 */
    min-height: 300px; /* 设置最小高度 */
    overflow: hidden;
}

.chart-container {
  grid-area: chart;
  width: 100%;
  height: 100%;
}

/* 更全面的深度选择器以控制 Plotly 生成的元素 */
:deep(.js-plotly-plot) {
  width: 100% !important;
  height: 100% !important;
  overflow: hidden !important;
}

:deep(.plot-container) {
  width: 100% !important;
  height: 100% !important;
  overflow: hidden !important;
}

:deep(.main-svg) {
  width: 100% !important;
  height: 100% !important;
  overflow: visible !important;  /* 改为visible确保图表内容可见 */
}

/* 覆盖其他可能导致滚动的元素 */
:deep(.svg-container) {
  overflow: visible !important;  /* 改为visible确保图表内容可见 */
}

.chart-overlay {
  grid-area: chart;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-error {
  color: red;
}

/* 确保所有Plotly相关元素都能自适应 */
:deep(.js-plotly-plot),
:deep(.plot-container),
:deep(.svg-container) {
  width: 100% !important;
  height: 100% !important;
  max-width: 100% !important;
  max-height: 100% !important;
}

:deep(.main-svg) {
  width: 100% !important;
  height: 100% !important;
}

</style>