<script setup lang="ts">
import { ref, computed } from 'vue';
import { useElementSize } from '@vueuse/core';
import { useKeypress } from 'vue3-keypress';

import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();

import PaperInformation from 'src/components/PaperInformation.vue';
import PaperList from 'src/components/PaperList.vue';
import FilterPanel from 'src/components/FilterPanel.vue';

import { useGlobalStore } from 'src/stores/globalStore';
const globalStore = useGlobalStore();

const rightDrawerOpen = computed(() => paperDataStore.selectedPaper !== null);

const container = ref(null);
const { width: containerWidth, height: outerContainerHeight } =
  useElementSize(container);

useKeypress({
  keyEvent: 'keydown',
  keyBinds: [
    {
      keyCode: 'left',
      success: previousPaper,
      preventDefault: false,
    },
    {
      keyCode: 'right',
      success: nextPaper,
      preventDefault: false,
    },
    {
      keyCode: 'up',
      success: focusPreviousPaper,
      // preventDefault: false,
    },
    {
      keyCode: 'down',
      success: focusNextPaper,
      // preventDefault: false,
    },
  ],
});

function previousPaper() {
  if (paperDataStore.selectedPaper === null) return;
  paperDataStore.previousPaper();
}
function nextPaper() {
  if (paperDataStore.selectedPaper === null) return;
  paperDataStore.nextPaper();
}

function focusPreviousPaper() {
  paperDataStore.focusPreviousPaper();
}
function focusNextPaper() {
  paperDataStore.focusNextPaper();
}
</script>

<template>
  <q-drawer v-model="globalStore.filterPanelOpen" side="left">
    <FilterPanel />
  </q-drawer>

  <q-drawer
    no-swipe-open
    no-swipe-close
    no-swipe-backdrop
    v-model="rightDrawerOpen"
    side="right"
    overlay
    :width="containerWidth"
    v-touch-swipe.left="nextPaper"
    v-touch-swipe.right="previousPaper"
  >
    <PaperInformation />
  </q-drawer>
  <q-page-container>
    <q-page ref="container" class="items-center">
      <PaperList v-if="paperDataStore.allData" />
      <div class="q-ma-lg" v-else>loading...</div>
    </q-page>
  </q-page-container>
</template>
