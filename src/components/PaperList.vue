<script setup lang="ts">
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();
</script>

<template>
  <q-list v-if="paperDataStore.allData">
    <template v-for="paperInfo in paperDataStore.allData" :key="paperInfo.doi">
      <q-item>
        <q-item-section>
          <q-item-label>{{ paperInfo.title }}</q-item-label>
          <q-item-label caption lines="2">{{
            paperDataStore.getAuthors(paperInfo).join(', ')
          }}</q-item-label>
        </q-item-section>

        <q-item-section side top>
          <q-item-label caption>{{
            `${paperDataStore.getConference(paperInfo)}, ${paperInfo.year}`
          }}</q-item-label>
          <q-item-label v-if="paperInfo.award"
            >{{ paperDataStore.getAward(paperInfo) }}
            <q-icon name="emoji_events" color="primary" size="xs" />
          </q-item-label>
        </q-item-section>
      </q-item>
      <q-separator spaced inset />
    </template>
  </q-list>
</template>

<style scoped lang="scss"></style>
