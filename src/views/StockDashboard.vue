<!-- src/views/StockDashboard.vue -->
<template>
  <div class="stock-dashboard-page">
    <dashboard />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import Dashboard from '@/components/dashboard/Dashboard.vue';

export default defineComponent({
  name: 'StockDashboardPage',
  components: {
    Dashboard
  }
});
</script>

<style scoped>
.stock-dashboard-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}
</style>