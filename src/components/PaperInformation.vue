<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();
</script>

<template>
  <div v-if="paperDataStore.selectedPaper">
    {{ paperDataStore.selectedPaper.title }}
  </div>
  <div v-else>no paper selected</div>
</template>

<style scoped lang="scss"></style>
