<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps<{
  count: number;
  maxCount: number;
}>();
</script>

<template>
  <div class="underline">
    <div
      class="underline-data"
      :style="`width: ${
        props.maxCount === 0 ? 0 : (100 * props.count) / props.maxCount
      }%`"
    ></div>
  </div>
</template>

<style scoped lang="scss">
.underline {
  background: rgba(125, 125, 125, 0.2);
  height: 2px;
}

.underline-data {
  background-color: $primary;
  height: 2px;
}
</style>
