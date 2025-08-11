<template>
<div class="chart-wrapper">
    <!-- 标题和选择器行 -->
    <div class="chart-header">
      <div class="chart-title">{{ chartTitle || '图表' }}</div>
      <div class="selector-group" v-if="showSectorSelector || showDatePicker">
        <!-- 单日选择器 -->
        <div class="single-date-selector" v-if="showDatePicker">
          <div class="single-date-container">
            <label>{{ datePickerLabel }}：</label>
            <input 
              type="date" 
              v-model="selectedDate" 
              @change="onSingleDateChange"
              class="date-input"
              :max="getCurrentDate()"
            />
          </div>
        </div>
        
        <!-- 日期范围选择器 -->
        <div class="date-selector" v-if="showSectorSelector">
          <div class="date-range-container">
            <div class="date-input-group">
              <label>开始日期：</label>
              <input 
                type="date" 
                v-model="selectedStartDate" 
                @change="onDateRangeChange"
                class="date-input"
                :max="selectedEndDate || getCurrentDate()"
              />
            </div>
            <div class="date-input-group">
                <label>结束日期：</label>
                <input 
                  type="date" 
                  v-model="selectedEndDate" 
                  @change="onDateRangeChange"
                  class="date-input"
                  :min="selectedStartDate"
                  :max="getCurrentDate()"
                />
              </div>
              <div class="date-shortcuts">
                <button @click="setDateRange(30)" class="date-shortcut-btn">最近30天</button>
                <button @click="setDateRange(60)" class="date-shortcut-btn">最近60天</button>
                <button @click="setDateRange(90)" class="date-shortcut-btn">最近90天</button>
              </div>
            </div>
          </div>
          
          <!-- 板块选择器 -->
          <div class="sector-selector" v-if="sectorInfo && sectorInfo.availableSectors">
            <div class="sector-select-group">
              <label>选择板块：</label>
              <select v-model="selectedSector" @change="onSectorChange">
                <option v-for="sector in sectorInfo.availableSectors" 
                        :key="sector" 
                        :value="sector">
                  {{ sector }}
                </option>
              </select>
              <span class="sector-count">(共{{ sectorInfo.sectorCount }}个板块)</span>
            </div>
            <div class="sector-input-group">
              <label>或输入板块：</label>
              <input 
                type="text" 
                v-model="customSectorName" 
                placeholder="请输入板块名称"
                class="sector-input"
                @keyup.enter="addCustomSector"
              />
              <button @click="addCustomSector" class="add-sector-btn">确定</button>
            </div>
          </div>
        </div>
    </div>
    
    <!-- 图表容器 -->
    <div class="chart-container" ref="chartContainer">
      <!-- 加载中或错误覆盖层 - 只在图表容器内显示 -->
      <div v-if="loading" class="chart-overlay chart-loading">
        <div class="loading-content">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>
      </div>
      <div v-else-if="error" class="chart-overlay chart-error">{{ error }}</div>
    </div>
</div>
</template>
  
  <script>
  import { defineComponent, ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue';
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
      const loading = ref(false); // 初始不显示加载状态
      const error = ref(null);
      const chartData = ref(null);
      
      // 板块选择相关状态
      const selectedSector = ref(null);
      const customSectorName = ref('');
      const sectorInfo = ref(null);
      
      // 图表标题 - 只使用配置中的标题，不使用API返回的layout.title以避免重复
      const chartTitle = computed(() => {
        // 使用组件配置中的标题
        if (props.componentConfig && props.componentConfig.title) {
          return props.componentConfig.title;
        }
        // 使用默认标题
        return '图表';
      });
      
      // 日期选择相关状态
      const selectedStartDate = ref('2025-07-01');
      const selectedEndDate = ref(getCurrentDate());
      const dateRangeInfo = ref(null);
      
      // 单日选择器相关状态
      const selectedDate = ref(getCurrentDate());
      
      // 获取当前日期的方法
      function getCurrentDate() {
        return new Date().toISOString().split('T')[0];
      }
      
      // 计算是否显示单日选择器
      const showDatePicker = computed(() => {
        return props.componentConfig && props.componentConfig.supports_date_picker === true;
      });
      
      // 计算日期选择器标签
      const datePickerLabel = computed(() => {
        return props.componentConfig?.date_picker_label || '选择日期';
      });
      
      // 单日选择器变化处理
      const onSingleDateChange = () => {
        console.log('单日选择器变化:', selectedDate.value);
        loadChartData();
      };
      
      // 设置日期范围的快捷方法
      const setDateRange = (days) => {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - days);
        
        selectedEndDate.value = endDate.toISOString().split('T')[0];
        selectedStartDate.value = startDate.toISOString().split('T')[0];
        
        // 触发数据重新加载
        onDateRangeChange();
      };
      
      // 计算是否显示板块选择器
      const showSectorSelector = computed(() => {
        return props.componentConfig && props.componentConfig.supportsSectorSelection === true;
      });
      
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
      
      // 板块选择改变处理函数
      const onSectorChange = () => {
        console.log('板块选择改变:', selectedSector.value);
        loadChartData();
      };
      
      // 添加自定义板块
      const addCustomSector = () => {
        const inputSector = customSectorName.value.trim();
        if (!inputSector) {
          alert('请输入板块名称');
          return;
        }
        
        // 检查是否已存在 - 如果存在则直接选择，不报错
        if (sectorInfo.value && sectorInfo.value.availableSectors && 
            sectorInfo.value.availableSectors.includes(inputSector)) {
          // 直接选择该板块，不显示错误信息
          selectedSector.value = inputSector;
          customSectorName.value = '';
          onSectorChange(); // 触发数据加载
          return;
        }
        
        // 添加到可用板块列表
        if (sectorInfo.value && sectorInfo.value.availableSectors) {
          sectorInfo.value.availableSectors.unshift(inputSector);
          sectorInfo.value.sectorCount = sectorInfo.value.availableSectors.length;
        } else {
          // 如果还没有sectorInfo，创建一个
          sectorInfo.value = {
            availableSectors: [inputSector],
            sectorCount: 1,
            currentSector: inputSector
          };
        }
        
        // 选择新添加的板块
        selectedSector.value = inputSector;
        customSectorName.value = '';
        
        // 重新加载图表数据
        console.log('添加自定义板块:', inputSector);
        loadChartData();
      };
      
      // 日期范围选择改变处理函数
      const onDateRangeChange = () => {
        console.log('日期范围选择改变:', selectedStartDate.value);
        loadChartData();
      };
      
      const loadChartData = async (url) => {
        // 添加一个最小加载时间，防止loading状态闪烁
        const startTime = Date.now();
        const minLoadingTime = 300; // 最小加载时间300ms
        
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
          
          // 如果支持板块选择且已选择板块，添加sector参数
          if (showSectorSelector.value && selectedSector.value) {
            urlObj.searchParams.set('sector', selectedSector.value);
            console.log('添加sector参数:', selectedSector.value);
          }
          
          // 如果支持单日选择器且已选择日期，添加date参数
          if (showDatePicker.value && selectedDate.value) {
            urlObj.searchParams.set('date', selectedDate.value);
            console.log('添加date参数:', selectedDate.value);
          }
          
          // 如果支持日期范围选择且已选择日期，添加日期范围参数
          if (showSectorSelector.value && selectedStartDate.value) {
            urlObj.searchParams.set('startDate', selectedStartDate.value);
            console.log('添加startDate参数:', selectedStartDate.value);
          }
          
          if (showSectorSelector.value && selectedEndDate.value) {
            urlObj.searchParams.set('endDate', selectedEndDate.value);
            console.log('添加endDate参数:', selectedEndDate.value);
          }
          
          const finalUrl = urlObj.toString();
          console.log('最终请求URL:', finalUrl);
          
          const response = await axios.get(finalUrl);
          chartData.value = response.data;
          console.log('收到的图表数据:', chartData.value);
          
          // 处理板块信息（如果存在）
          if (showSectorSelector.value && chartData.value.sectorInfo) {
            sectorInfo.value = chartData.value.sectorInfo;
            // 如果没有选中的板块，使用当前板块作为默认值
            if (!selectedSector.value) {
              selectedSector.value = chartData.value.sectorInfo.currentSector;
            }
            console.log('更新板块信息:', sectorInfo.value);
          }
          
          // 处理日期范围信息（如果存在）
          if (showSectorSelector.value && chartData.value.dateRangeInfo) {
            dateRangeInfo.value = chartData.value.dateRangeInfo;
            // 如果没有选中的开始日期，使用当前开始日期作为默认值
            if (!selectedStartDate.value) {
              selectedStartDate.value = chartData.value.dateRangeInfo.currentStartDate;
            }
            console.log('更新日期范围信息:', dateRangeInfo.value);
          }
          
          // 确保最小加载时间，防止闪烁
          const elapsedTime = Date.now() - startTime;
          const remainingTime = Math.max(0, minLoadingTime - elapsedTime);
          
          setTimeout(() => {
            // 先将 loading 设为 false，让容器渲染出来
            loading.value = false;
            
            // 使用 nextTick 确保 DOM 已更新后再渲染图表
            nextTick(() => {
              console.log('nextTick 后检查容器:', chartContainer.value);
              renderChart();
            });
          }, remainingTime);
        } catch (err) {
          // 错误情况也要等待最小时间
          const elapsedTime = Date.now() - startTime;
          const remainingTime = Math.max(0, minLoadingTime - elapsedTime);
          
          setTimeout(() => {
            error.value = `加载图表数据失败: ${err.message}`;
            console.error('获取图表数据出错:', err);
            loading.value = false;
          }, remainingTime);
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
        // 注意：堆叠条形图（barmode: "stack"）不应该排序，因为需要保持固定的堆叠顺序
        if (traces.length > 1 && layoutConfig.barmode !== 'stack') {
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
                t: 50,   // 顶部边距，减少因为标题现在在外部
                b: 120,  // 底部边距，为x轴标签留空间（增大以适应倾斜标签）
                pad: 4
            },
            // 动态设置宽高以适应容器
            width: chartContainer.value.clientWidth,
            height: chartContainer.value.clientHeight || 600,
            // 确保坐标轴能自动调整范围显示所有数据
            yaxis: {
                autorange: true,     // 自动调整y轴范围显示所有数据
                fixedrange: false,   // 允许缩放以便查看细节
                ...layoutConfig.yaxis
            },
            xaxis: {
                autorange: true,     // 自动调整x轴范围显示所有数据
                fixedrange: false,   // 允许缩放以便查看细节
                automargin: true,    // 自动调整边距以适应标签
                ...layoutConfig.xaxis
            },
            // 图例设置，避免被裁剪
            legend: {
                orientation: "h",    // 水平排列图例
                x: 0,
                y: -0.2,            // 放在图表下方，增大间距
                xanchor: 'left',
                yanchor: 'top',
                ...layoutConfig.legend
            },
            // 后端配置会覆盖上面的默认配置
            ...layoutConfig,
            // 移除图表内部标题，因为我们已经在上方有了优化的标题栏
            title: undefined
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
        getComponentDelay,
        // 图表标题
        chartTitle,
        // 板块选择相关
        showSectorSelector,
        selectedSector,
        customSectorName,
        sectorInfo,
        onSectorChange,
        addCustomSector,
        // 日期范围选择相关
        selectedStartDate,
        selectedEndDate,
        dateRangeInfo,
        onDateRangeChange,
        getCurrentDate,
        setDateRange,
        // 单日选择器相关
        showDatePicker,
        selectedDate,
        datePickerLabel,
        onSingleDateChange
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

.chart-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 图表包装器样式 */
.chart-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

/* 图表头部样式 */
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  min-height: 40px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0;
  flex-shrink: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 选择器组合样式 - 在标题行中 */
.selector-group {
  display: flex;
  flex-direction: row;
  gap: 15px;
  align-items: center;
  flex-shrink: 0;
}

.chart-container {
  flex: 1;
  width: 100%;
  height: calc(100% - 60px); /* 减去header的高度 */
  position: relative;
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
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 999;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 14px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

/* 板块选择器样式 - 在标题行中使用 */
.sector-selector {
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

/* 单日选择器样式 */
.single-date-selector {
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

.single-date-container {
  display: flex;
  align-items: center;
  gap: 6px;
}

.single-date-container label {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-size: 12px;
  white-space: nowrap;
  min-width: 60px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.single-date-container input[type="date"] {
  padding: 4px 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: white;
  font-size: 12px;
  color: #495057;
  min-width: 130px;
}

.single-date-container input[type="date"]:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.15rem rgba(0, 123, 255, 0.25);
}

.sector-select-group,
.sector-input-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.sector-input {
  padding: 3px 6px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: white;
  font-size: 11px;
  color: #495057;
  min-width: 100px;
  max-width: 120px;
}

.sector-input:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.15rem rgba(0, 123, 255, 0.25);
}

.add-sector-btn {
  padding: 3px 8px;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.add-sector-btn:hover {
  background: linear-gradient(135deg, #ff5252 0%, #d63031 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.add-sector-btn:active {
  background-color: #004085;
}

/* 日期选择器样式 - 在标题行中使用 */
.date-selector {
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

.date-range-container {
  display: flex;
  flex-direction: column;
  gap: 3px;  /* 进一步减少间距 */
}

.date-input-group {
  display: flex;
  align-items: center;
  gap: 4px;  /* 减少组内间距 */
}

.date-input-group label {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-size: 11px;
  white-space: nowrap;
  min-width: 50px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.sector-selector label,
.date-selector label {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-size: 12px;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.sector-selector select,
.date-selector select,
.date-selector input[type="date"] {
  padding: 3px 6px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: white;
  font-size: 11px;
  color: #495057;
  min-width: 100px;
  max-width: 120px;
}

.sector-selector select:focus,
.date-selector select:focus,
.date-selector input[type="date"]:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.15rem rgba(0, 123, 255, 0.25);
}

.date-shortcuts {
  display: flex;
  gap: 3px;
  margin-top: 4px;
  justify-content: center;
}

.date-shortcut-btn {
  padding: 2px 6px;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  color: white;
  border: none;
  border-radius: 3px;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.date-shortcut-btn:hover {
  background: linear-gradient(135deg, #0984e3 0%, #0574c7 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.date-shortcut-btn:active {
  background-color: #495057;
}

.sector-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 10px;
  font-style: italic;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

</style>