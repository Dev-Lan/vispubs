<script setup lang="ts">
import { computed } from 'vue';
import { usePaperDataStore } from 'src/stores/paperDataStore';
import { useAuthorStore } from 'src/stores/authorStore';
import Highlighter from 'vue-highlight-words';
const paperDataStore = usePaperDataStore();
const authorStore = useAuthorStore();
function authorHasWebsite(author: string): boolean {
  return (
    !authorStore.loading &&
    (authorStore.websites.has(author) ||
      authorStore.websites.has(author + ' 0001')) // future-proof in case there is a new publisher with the same name.
  );
}

function getAuthorWebsite(author: string): string {
  if (authorStore.websites.has(author))
    return authorStore.websites.get(author)!;
  return authorStore.websites.get(author + ' 0001')!;
}

function getAuthorFormLink(author: string): string {
  const encodedName = encodeURIComponent(author);
  return `https://docs.google.com/forms/d/e/1FAIpQLSfjSiQs92GtpDRItX69tFdmu0teSIFZPs5pXenoy3untsKV2Q/viewform?usp=pp_url&entry.1065422414=${encodedName}`;
}

const caseSensitive = computed(() => {
  return paperDataStore.matchCase ? true : false;
});
const autoEscape = computed(() => {
  return paperDataStore.useRegex ? false : true;
});

const searchWords = computed(() => {
  return [paperDataStore.searchText];
});
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

  <div v-if="paperDataStore.selectedPaper" class="q-mt-sm q-mx-lg q-mb-lg">
    <div class="text-h5 text-center">
      <q-btn
        :href="`https://doi.org/${paperDataStore.selectedPaper.doi}`"
        target="_blank"
        icon-right="open_in_new"
        flat
        no-caps
        size="lg"
      >
        <Highlighter
          highlightClassName="highlight"
          :searchWords="searchWords"
          :autoEscape="autoEscape"
          :caseSensitive="caseSensitive"
          :textToHighlight="paperDataStore.selectedPaper.title"
        />
      </q-btn>
    </div>
    <div class="q-mb-sm q-mx-sm flex justify-center items-center">
      <div>
        {{
          `${paperDataStore.getConference(paperDataStore.selectedPaper)}, ${
            paperDataStore.selectedPaper.year
          }`
        }}
      </div>
      <q-badge
        outline
        v-if="paperDataStore.selectedPaper.award"
        color="positive"
        class="q-ml-lg"
        >{{ paperDataStore.getAward(paperDataStore.selectedPaper) }}
        <q-icon name="emoji_events" color="positive" size="xs" />
      </q-badge>
    </div>
    <div class="q-mb-md q-mx-sm flex justify-center">
      <template
        v-for="(
          { displayName, dedupedName }, index
        ) in paperDataStore.getAuthors(paperDataStore.selectedPaper)"
        :key="index"
      >
        <q-btn
          v-if="authorHasWebsite(dedupedName)"
          :href="getAuthorWebsite(dedupedName)"
          target="_blank"
          icon-right="open_in_new"
          flat
          no-caps
        >
          <Highlighter
            highlightClassName="highlight"
            :searchWords="searchWords"
            :autoEscape="autoEscape"
            :caseSensitive="caseSensitive"
            :textToHighlight="displayName"
        /></q-btn>
        <q-btn
          v-else
          :href="getAuthorFormLink(dedupedName)"
          target="_blank"
          icon-right="help"
          flat
          no-caps
          size="md"
          ><Highlighter
            highlightClassName="highlight"
            :searchWords="searchWords"
            :autoEscape="autoEscape"
            :textToHighlight="displayName"
        /></q-btn>
      </template>
    </div>
    <div class="flex flex-center">
      <div class="mw-600">
        <Highlighter
          highlightClassName="highlight"
          :searchWords="searchWords"
          :autoEscape="autoEscape"
          :caseSensitive="caseSensitive"
          :textToHighlight="paperDataStore.selectedPaper.abstract"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.mw-600 {
  max-width: 600px;
}
</style>
