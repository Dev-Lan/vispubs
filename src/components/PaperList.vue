<script setup lang="ts">
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();
</script>

<template>
  <q-list v-if="paperDataStore.allData">
    <q-item v-for="paperInfo in paperDataStore.allData" :key="paperInfo.doi">
      <q-item-section>
        <q-item-label>{{ paperInfo.title }}</q-item-label>
        <q-item-label caption lines="2">{{
          paperInfo.authorNames
        }}</q-item-label>
      </q-item-section>

      <q-item-section side top>
        <q-item-label caption>{{
          `${paperInfo.conference}, ${paperInfo.year}`
        }}</q-item-label>
        <span v-if="paperInfo.award">
          <span>{{ paperInfo.award }} </span>
          <q-icon name="emoji_events" color="primary" size="xs" />
        </span>
      </q-item-section>
    </q-item>
    <q-separator spaced inset />
  </q-list>
</template>

<style scoped lang="scss"></style>
