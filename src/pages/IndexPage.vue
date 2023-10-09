<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useElementSize } from '@vueuse/core';

import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();

import PaperInformation from 'src/components/PaperInformation.vue';
import PaperList from 'src/components/PaperList.vue';

const rightDrawerOpen = computed(() => paperDataStore.selectedPaper !== null);

const container = ref(null);
const { width: containerWidth, height: outerContainerHeight } =
  useElementSize(container);
</script>

<template>
  <q-page ref="container" class="row items-center justify-evenly">
    <PaperList />
  </q-page>
  <q-drawer
    v-model="rightDrawerOpen"
    side="right"
    overlay
    :width="containerWidth"
  >
    <PaperInformation />
  </q-drawer>
</template>
