<script setup lang="ts">
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();
</script>

<template>
  <q-virtual-scroll
    :items="paperDataStore.allData"
    bordered
    separator
    v-slot="{ item }"
  >
    <q-item
      :key="item.doi"
      clickable
      v-ripple
      @click="paperDataStore.selectedPaper = item"
    >
      <q-item-section>
        <q-item-label>{{ item.title }}</q-item-label>
        <q-item-label caption lines="2">{{
          paperDataStore.getAuthors(item).join(', ')
        }}</q-item-label>
      </q-item-section>

      <q-item-section side top>
        <q-item-label caption>{{
          `${paperDataStore.getConference(item)}, ${item.year}`
        }}</q-item-label>
        <q-item-label v-if="item.award"
          >{{ paperDataStore.getAward(item) }}
          <q-icon name="emoji_events" color="primary" size="xs" />
        </q-item-label>
      </q-item-section>
    </q-item>
  </q-virtual-scroll>
</template>

<style scoped lang="scss"></style>
