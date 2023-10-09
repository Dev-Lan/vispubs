<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { usePaperDataStore } from 'src/stores/paperDataStore';
import { useAuthorStore } from 'src/stores/authorStore';
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
      <template
        v-for="(
          { displayName, dedupedName }, index
        ) in paperDataStore.getAuthors(paperDataStore.selectedPaper)"
        :key="index"
      >
        <q-btn
          v-if="authorHasWebsite(dedupedName)"
          :href="getAuthorWebsite(dedupedName)"
          :label="displayName"
          target="_blank"
          icon-right="open_in_new"
          flat
        />
        <q-btn
          v-else
          :href="getAuthorFormLink(dedupedName)"
          :label="displayName"
          target="_blank"
          icon-right="help"
          flat
        />
      </template>
    </div>
    <div>
      {{ paperDataStore.selectedPaper.abstract }}
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
