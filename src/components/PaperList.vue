<script setup lang="ts">
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();

// guaranteed to be loaded because of the v-if in the parent
// not sure the impact but Quasar docs suggest to not use responsive
// objects https://quasar.dev/vue-components/virtual-scroll#qvirtualscroll-api
const papers = JSON.parse(JSON.stringify(paperDataStore.allData));
const offset = 50 * 2; // height of header + inner toolbar
</script>

<template>
  <q-toolbar>
    <q-badge color="primary" outline>{{ papers.length }} papers</q-badge>
    <!-- warning: if spacing is changed, offset will have to change -->
    <q-space />
  </q-toolbar>
  <q-virtual-scroll
    :items="papers"
    bordered
    separator
    v-slot="{ item, index }"
    class="flex-grow-1"
    :style="`max-height: calc(100vh - ${offset}px);`"
  >
    <q-item
      :key="item.doi"
      clickable
      v-ripple
      @click="paperDataStore.selectPaper(index)"
    >
      <q-item-section>
        <q-item-label>
          <q-badge color="primary" outline>{{ index + 1 }}</q-badge>
          {{ item.title }}</q-item-label
        >
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

<style scoped lang="scss">
.flex-grow-1 {
  flex-grow: 1;
}
</style>
