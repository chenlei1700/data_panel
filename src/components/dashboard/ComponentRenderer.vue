<template>
    <div class="component-container">
      <!-- 隐藏默认的灰色标题栏，因为图表组件内部已经有了更好看的蓝色渐变标题栏 -->
      <!-- <div class="component-header">
        <h3>{{ componentConfig.title }}</h3>
      </div> -->
      <div class="component-content">
        <component 
          :is="componentType" 
          :component-config="componentConfig"
          ref="contentComponent"
        />
      </div>
    </div>
  </template>
  
  <script>
  import { defineComponent, computed, ref } from 'vue';
  import ChartComponent from './ChartComponent.vue';
  import TableComponent from './TableComponent.vue';
  import StackedAreaChartComponent from './StackedAreaChartComponent.vue';
    
  export default defineComponent({
    name: 'ComponentRenderer',
    components: {
      ChartComponent,
      TableComponent,
      StackedAreaChartComponent
    },
    props: {
      componentConfig: {
        type: Object,
        required: true
      }
    },
    setup(props, { expose }) { // Add the { expose } context parameter
      const contentComponent = ref(null);
      
      const componentType = computed(() => {
        switch (props.componentConfig.type) {
          case 'chart':
            return 'ChartComponent';
          case 'table':
            return 'TableComponent';
          case 'stackedAreaChart':
            return 'StackedAreaChartComponent';
          default:
            return null;
        }
      });
      
      // Move the updateDataSource function inside the setup
      const updateDataSource = (newParams) => {
        // 解析当前数据源URL
        const url = new URL(props.componentConfig.dataSource, window.location.origin);
        
        // 更新参数
        Object.entries(newParams).forEach(([key, value]) => {
          url.searchParams.set(key, value);
        });
        
        // 通过ref访问子组件并调用其方法
        if (contentComponent.value && typeof contentComponent.value.fetchData === 'function') {
          contentComponent.value.fetchData(url.pathname + url.search);
        }
      };
    
      // 使用expose方法暴露函数给父组件
      expose({ updateDataSource });
    
      return {
        componentType,
        contentComponent
      };
    }
  });
  </script>
  
  <style scoped>
  .component-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }
  
  .component-header {
    padding: 10px 15px;
    background-color: #f5f5f5;
    border-bottom: 1px solid #ddd;
  }
  
  .component-header h3 {
    margin: 0;
    font-size: 16px;
  }
  
  .component-content {
    flex: 1;
    height: 100%; /* 占满整个容器高度 */
    overflow: auto;
    /* 移除了 padding，因为图表组件内部已经有了合适的布局 */
  }
  </style>