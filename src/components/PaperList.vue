<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();
</script>

<template>
  <div v-if="paperDataStore.allData">
    <div>Title: {{ paperDataStore.allData[0].title }}</div>
    <div>Authors: {{ paperDataStore.allData[0].authorNames }}</div>
  </div>
</template>

<style scoped lang="scss"></style>
