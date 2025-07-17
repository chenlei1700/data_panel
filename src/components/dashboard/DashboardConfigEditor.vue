<template>
    <div class="config-editor">
      <h2>仪表盘配置</h2>
      
      <div class="form-group">
        <label>行数:</label>
        <input type="number" v-model.number="localConfig.rows" min="1" max="4" />
      </div>
      
      <div class="form-group">
        <label>列数:</label>
        <input type="number" v-model.number="localConfig.cols" min="1" max="4" />
      </div>
      
      <h3>组件</h3>
      <div v-for="(component, index) in localConfig.components" :key="index" class="component-config">
        <h4>{{ component.title }}</h4>
        
        <div class="form-group">
          <label>位置:</label>
          <div class="position-inputs">
            <div>
              <label>行:</label>
              <input type="number" v-model.number="component.position.row" min="0" :max="localConfig.rows - 1" />
            </div>
            <div>
              <label>列:</label>
              <input type="number" v-model.number="component.position.col" min="0" :max="localConfig.cols - 1" />
            </div>
            <div>
              <label>行跨度:</label>
              <input type="number" v-model.number="component.position.rowSpan" min="1" :max="localConfig.rows - component.position.row" />
            </div>
            <div>
              <label>列跨度:</label>
              <input type="number" v-model.number="component.position.colSpan" min="1" :max="localConfig.cols - component.position.col" />
            </div>
          </div>
        </div>
        
        <button @click="removeComponent(index)" class="remove-btn">删除</button>
      </div>
      
      <div class="add-component">
        <h3>添加新组件</h3>
        <div class="form-group">
          <label>类型:</label>
          <select v-model="newComponent.type">
            <option value="chart">图表</option>
            <option value="table">表格</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>标题:</label>
          <input type="text" v-model="newComponent.title" />
        </div>
        
        <div class="form-group">
          <label>数据源:</label>
          <input type="text" v-model="newComponent.dataSource" />
        </div>
        
        <div class="form-group">
          <label>位置:</label>
          <div class="position-inputs">
            <div>
              <label>行:</label>
              <input type="number" v-model.number="newComponent.position.row" min="0" :max="localConfig.rows - 1" />
            </div>
            <div>
              <label>列:</label>
              <input type="number" v-model.number="newComponent.position.col" min="0" :max="localConfig.cols - 1" />
            </div>
            <div>
              <label>行跨度:</label>
              <input type="number" v-model.number="newComponent.position.rowSpan" min="1" :max="localConfig.rows - newComponent.position.row" />
            </div>
            <div>
              <label>列跨度:</label>
              <input type="number" v-model.number="newComponent.position.colSpan" min="1" :max="localConfig.cols - newComponent.position.col" />
            </div>
          </div>
        </div>
        
        <button @click="addComponent" class="add-btn">添加</button>
      </div>
      
      <div class="actions">
        <button @click="applyConfig" class="apply-btn">应用配置</button>
      </div>
    </div>
  </template>
  
  <script>
  import { defineComponent, ref, reactive, computed, watch } from 'vue';
  
  export default defineComponent({
    name: 'DashboardConfigEditor',
    props: {
      config: {
        type: Object,
        required: true
      }
    },
    emits: ['update:config'],
    setup(props, { emit }) {
      const localConfig = ref({...props.config});
      
      const newComponent = reactive({
        id: '',
        type: 'chart',
        title: '',
        dataSource: '',
        position: {
          row: 0,
          col: 0,
          rowSpan: 1,
          colSpan: 1
        }
      });
      
      const addComponent = () => {
        if (!newComponent.title || !newComponent.dataSource) {
          alert('请填写标题和数据源');
          return;
        }
        
        // 生成唯一ID
        newComponent.id = `component-${Date.now()}`;
        
        // 添加新组件
        localConfig.value.components.push({...newComponent});
        
        // 重置表单
        newComponent.title = '';
        newComponent.dataSource = '';
        newComponent.type = 'chart';
        newComponent.position = {
          row: 0,
          col: 0,
          rowSpan: 1,
          colSpan: 1
        };
      };
      
      const removeComponent = (index) => {
        localConfig.value.components.splice(index, 1);
      };
      
      const applyConfig = () => {
        emit('update:config', localConfig.value);
      };
      
      // 监听原始配置变化
      watch(() => props.config, (newConfig) => {
        localConfig.value = {...newConfig};
      }, { deep: true });
      
      return {
        localConfig,
        newComponent,
        addComponent,
        removeComponent,
        applyConfig
      };
    }
  });
  </script>
  
  <style scoped>
  .config-editor {
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
  }
  
  input, select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    width: 100%;
  }
  
  .position-inputs {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 10px;
  }
  
  .component-config {
    margin-bottom: 20px;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
  }
  
  .add-component {
    margin-top: 20px;
    padding: 15px;
    border: 1px dashed #aaa;
    border-radius: 4px;
  }
  
  .actions {
    margin-top: 20px;
    text-align: right;
  }
  
  button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
  }
  
  .add-btn {
    background-color: #4CAF50;
    color: white;
  }
  
  .remove-btn {
    background-color: #f44336;
    color: white;
  }
  
  .apply-btn {
    background-color: #2196F3;
    color: white;
  }
  </style>