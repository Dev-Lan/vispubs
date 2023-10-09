<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();

import PaperInformation from 'src/components/PaperInformation.vue';
import PaperList from 'src/components/PaperList.vue';

const rightDrawerOpen = computed(() => paperDataStore.selectedPaper !== null);
const fullWidth = ref(1294); //TODO: watch window size
</script>

<template>
  <q-page class="row items-center justify-evenly">
    <PaperList />
  </q-page>
  <q-drawer v-model="rightDrawerOpen" side="right" overlay :width="fullWidth">
    <PaperInformation />
  </q-drawer>
</template>
