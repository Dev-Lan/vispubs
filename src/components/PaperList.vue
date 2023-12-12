<script setup lang="ts">
import { computed } from 'vue';
import Highlighter from 'vue-highlight-words';
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();

const autoEscape = computed(() => {
  return paperDataStore.useRegex ? false : true;
});

const searchWords = computed(() => {
  return [paperDataStore.searchText];
});

const offset = 50 + 50; // height of header + inner toolbar
</script>

<template>
  <q-toolbar>
    <!-- warning: if spacing is changed, offset will have to change -->
    <q-input
      rounded
      outlined
      dense
      class="flex-grow-1 q-mr-md"
      label="Search (Title, Author, Abstract)"
      v-model="paperDataStore.searchText"
    >
      <template v-slot:append>
        <q-btn-toggle
          v-model="paperDataStore.matchCase"
          bordered
          no-caps
          rounded
          clearable
          toggle-color="primary"
          color="white"
          text-color="primary"
          dense
          size="sm"
          :options="[{ label: 'Match Case', value: 'true' }]"
        />

        <q-btn-toggle
          v-model="paperDataStore.useRegex"
          bordered
          no-caps
          rounded
          clearable
          toggle-color="primary"
          color="white"
          text-color="primary"
          dense
          size="sm"
          :options="[{ label: 'Use Regex', value: 'true' }]"
        />
        <q-icon v-if="paperDataStore.searchText === ''" name="search" />
        <q-icon
          v-else
          name="clear"
          class="cursor-pointer"
          @click="paperDataStore.searchText = ''"
        />
      </template>
    </q-input>

    <q-badge color="primary" outline
      >{{ paperDataStore.papers.length }} papers</q-badge
    >
  </q-toolbar>
  <q-virtual-scroll
    v-if="paperDataStore.papers.length > 0"
    :items="paperDataStore.papers"
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
          <Highlighter
            highlightClassName="highlight"
            :searchWords="searchWords"
            :autoEscape="autoEscape"
            :textToHighlight="item.title"
          />
        </q-item-label>
        <q-item-label caption lines="2">
          <Highlighter
            highlightClassName="highlight"
            :searchWords="searchWords"
            :autoEscape="autoEscape"
            :textToHighlight="
              paperDataStore
                .getAuthors(item)
                .map((d) => d.displayName)
                .join(', ')
            "
          />
        </q-item-label>
      </q-item-section>

      <q-item-section side top>
        <q-item-label caption
          ><span style="color: black">{{
            `${paperDataStore.getConference(item)}, ${item.year}`
          }}</span>
          [{{ index + 1 }}]</q-item-label
        >
        <q-badge v-if="item.award" color="positive" outline
          >{{ paperDataStore.getAward(item) }}
          <q-icon name="emoji_events" color="positive" size="xs" />
        </q-badge>
      </q-item-section>
    </q-item>
  </q-virtual-scroll>
  <q-card v-else flat bordered square>
    <q-card-section>
      <div class="text-h6">No papers found...</div>
      with {{ paperDataStore.useRegex ? 'Regex ' : '' }}"{{
        paperDataStore.searchText
      }}" in the <b>Title</b>, <b>Author List</b>, or <b>Abstract</b>.
    </q-card-section>
  </q-card>
</template>

<style scoped lang="scss">
.flex-grow-1 {
  flex-grow: 1;
}
</style>
