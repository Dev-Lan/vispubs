<script setup lang="ts">
import { useRouter } from 'vue-router';
const router = useRouter();
import { PaperInfo, usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();
</script>

<template>
  <q-virtual-scroll
    :items="paperDataStore.allData"
    bordered
    separator
    v-slot="{ item, index }"
  >
    <q-item
      :key="item.doi"
      clickable
      v-ripple
      @click="paperDataStore.selectPaper(index)"
    >
      <q-item-section>
        <q-item-label>{{ item.title }}</q-item-label>
        <q-item-label caption lines="2">{{
          paperDataStore
            .getAuthors(item)
            .map((d) => d.displayName)
            .join(', ')
        }}</q-item-label>
      </q-item-section>

      <q-item-section side top>
        <q-item-label caption>{{
          `${paperDataStore.getConference(item)}, ${item.year}`
        }}</q-item-label>
        <q-badge v-if="item.award" color="positive" outline
          >{{ paperDataStore.getAward(item) }}
          <q-icon name="emoji_events" color="positive" size="xs" />
        </q-badge>
      </q-item-section>
    </q-item>
  </q-virtual-scroll>
</template>

<style scoped lang="scss"></style>
