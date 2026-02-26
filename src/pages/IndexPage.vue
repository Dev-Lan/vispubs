<script setup lang="ts">
import { computed } from 'vue';
import { useWindowSize } from '@vueuse/core';
import { useKeypress } from 'vue3-keypress';

import { usePaperDataStore } from 'src/stores/paperDataStore';
import { useSeo } from 'src/composables/useSeo';
const paperDataStore = usePaperDataStore();
useSeo();

import PaperInformation from 'src/components/PaperInformation.vue';
import PaperList from 'src/components/PaperList.vue';
import FilterPanel from 'src/components/FilterPanel.vue';

const rightDrawerOpen = computed(() => paperDataStore.selectedPaper !== null);

const { width: windowWidth } = useWindowSize();

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
  <q-drawer
    no-swipe-open
    no-swipe-close
    no-swipe-backdrop
    v-model="paperDataStore.filterPanelOpen"
    persistent
    side="left"
    class="no-scroll-x"
  >
    <FilterPanel />
  </q-drawer>

  <q-drawer
    no-swipe-open
    no-swipe-close
    no-swipe-backdrop
    v-model="rightDrawerOpen"
    side="right"
    overlay
    :width="windowWidth"
    v-touch-swipe.left="nextPaper"
    v-touch-swipe.right="previousPaper"
  >
    <PaperInformation />
  </q-drawer>
  <q-page-container>
    <q-page class="items-center">
      <div v-if="paperDataStore.allData" :data-nosnippet="rightDrawerOpen ? '' : undefined">
        <PaperList />
      </div>
      <div v-else class="q-ma-lg">loading...</div>
    </q-page>
  </q-page-container>
</template>
<style lang="scss">
a {
  color: $primary;
}

.no-scroll-x {
  overflow-x: hidden;
}
</style>
