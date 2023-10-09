<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();
</script>

<template>
  <q-toolbar class="q-mt-sm">
    <q-btn
      round
      @click="paperDataStore.deselectPaper()"
      icon="arrow_back"
    ></q-btn>

    <q-space />

    <span>{{ paperDataStore.progressDisplay }}</span>
    <q-btn
      round
      @click="paperDataStore.previousPaper()"
      icon="chevron_left"
      class="q-ml-md"
    ></q-btn>
    <q-btn
      round
      @click="paperDataStore.nextPaper()"
      icon="chevron_right"
      class="q-ml-md"
    ></q-btn>
  </q-toolbar>

  <div v-if="paperDataStore.selectedPaper" class="q-ma-lg">
    <div class="text-h5 text-center">
      {{ paperDataStore.selectedPaper.title }}
    </div>
    <div class="q-ma-sm flex justify-center">
      <q-btn
        v-for="(author, index) in paperDataStore.getAuthors(
          paperDataStore.selectedPaper
        )"
        :key="index"
        href="https://www.google.com"
        :label="author"
        target="_blank"
        icon-right="open_in_new"
        flat
      />
    </div>
    <div>
      {{ paperDataStore.selectedPaper.abstract }}
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
