<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';

import PaperInformation from 'src/components/PaperInformation.vue';
import PaperList from 'src/components/PaperList.vue';

const rightDrawerOpen = ref(true);
const halfWidth = ref(600); //TODO: watch window size
</script>

<template>
  <q-page class="row items-center justify-evenly">
    <PaperList />
  </q-page>
  <q-drawer v-model="rightDrawerOpen" side="right" bordered :width="halfWidth">
    <PaperInformation />
  </q-drawer>
</template>
