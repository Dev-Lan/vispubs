<script setup lang="ts">
import { computed, ref } from 'vue';
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

function quoteText(text: string): string {
  return `"${text}"`;
}

const addResourcesShown = ref(false);
const authorModalShown = ref(false);
const selectedAuthor = ref<{ displayName: string; dedupedName: string }>({
  displayName: '',
  dedupedName: '',
});

function selectAuthor(displayName: string, dedupedName: string): void {
  selectedAuthor.value = {
    displayName,
    dedupedName,
  };
  authorModalShown.value = true;
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
        v-for="(award, index) in paperDataStore.getKeyList(
          paperDataStore.selectedPaper.award
        )"
        :key="index"
        color="positive"
        outline
        class="q-ml-xs"
        >{{ paperDataStore.getAward(award) }}
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
          @click="selectAuthor(displayName, dedupedName)"
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

      <q-dialog v-model="authorModalShown">
        <q-card>
          <q-card-section>
            Search for author on:
            <q-card-actions>
              <q-btn
                :href="`https://scholar.google.com/scholar?q=${selectedAuthor.displayName}`"
                target="_blank"
                no-caps
                flat
                >Google Scholar</q-btn
              >
              <q-btn
                :href="`https://www.google.com/search?q=${selectedAuthor.displayName}`"
                target="_blank"
                no-caps
                flat
                >Google</q-btn
              >
            </q-card-actions>
            <q-card-actions>
              <q-btn
                :href="`https://www.bing.com/search?q=${selectedAuthor.displayName}`"
                target="_blank"
                no-caps
                flat
                >Bing</q-btn
              >
              <q-btn
                :href="`https://www.duckduckgo.com/?q=${selectedAuthor.displayName}`"
                target="_blank"
                no-caps
                flat
                >DuckDuckGo</q-btn
              >
            </q-card-actions>
          </q-card-section>

          <q-card-section class="q-pb-none">
            Submit author information:
            <q-card-actions>
              <q-btn
                :href="getAuthorFormLink(selectedAuthor.dedupedName)"
                target="_blank"
                no-caps
                flat
                >Google Form</q-btn
              >
            </q-card-actions>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn label="Done" color="primary" v-close-popup />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>
    <div class="flex flex-center">
      <q-card flat bordered class="q-ml-md q-mr-md q-mb-md align-self-start">
        <q-card-section>
          <div class="text-h6">Resources</div>
        </q-card-section>

        <q-card-section class="q-pa-none q-pb-sm">
          <q-list dense>
            <q-item
              v-for="resourceLink in paperDataStore.selectedPaperResourceLinks"
              :key="resourceLink.name"
              clickable
              v-ripple
              :href="resourceLink.url"
              target="_blank"
            >
              <q-item-section avatar>
                <q-avatar
                  :color="paperDataStore.getResourceColor(resourceLink.icon)"
                  :text-color="
                    paperDataStore.getResourceTextColor(resourceLink.icon)
                  "
                  :icon="paperDataStore.getResourceIcon(resourceLink.icon)"
                  size="md"
                />
              </q-item-section>

              <q-item-section>{{ resourceLink.name }}</q-item-section>
            </q-item>

            <q-separator class="q-mt-md q-mb-md" />

            <q-item clickable v-ripple @click="addResourcesShown = true">
              <q-item-section avatar>
                <q-avatar
                  color="primary"
                  text-color="white"
                  icon="add"
                  size="md"
                />
              </q-item-section>

              <q-item-section>Add Resources</q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-card-section>
          Search for paper on:
          <q-card-actions>
            <q-btn
              :href="`https://scholar.google.com/scholar?q=${quoteText(
                paperDataStore.selectedPaper.title
              )}`"
              target="_blank"
              no-caps
              flat
              >Google Scholar</q-btn
            >
            <q-btn
              :href="`https://www.google.com/search?q=${quoteText(
                paperDataStore.selectedPaper.title
              )}`"
              target="_blank"
              no-caps
              flat
              >Google</q-btn
            >
          </q-card-actions>
          <q-card-actions>
            <q-btn
              :href="`https://www.bing.com/search?q=${quoteText(
                paperDataStore.selectedPaper.title
              )}`"
              target="_blank"
              no-caps
              flat
              >Bing</q-btn
            >
            <q-btn
              :href="`https://www.duckduckgo.com/?q=${quoteText(
                paperDataStore.selectedPaper.title
              )}`"
              target="_blank"
              no-caps
              flat
              >DuckDuckGo</q-btn
            >
          </q-card-actions>
        </q-card-section>
      </q-card>
      <q-dialog v-model="addResourcesShown">
        <q-card>
          <q-card-section>
            <div class="text-h6">Add additional resources</div>
          </q-card-section>

          <q-card-section class="q-pb-none flex column"
            >Review instructions for adding resources at
            <a
              href="https://github.com/Dev-Lan/vispubs/tree/main/public/data"
              target="_blank"
              >github.</a
            ></q-card-section
          >

          <q-card-section class="q-pb-none flex column"
            >Then update this paper's
            <a
              :href="`https://github.com/Dev-Lan/vispubs/tree/main/public/data/paperLinks/${paperDataStore.selectedPaper.doi}`"
              target="_blank"
              >resource file.</a
            >
          </q-card-section>

          <q-card-actions align="right">
            <q-btn label="Done" color="primary" v-close-popup />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <div class="mw-600 align-self-start">
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

.align-self-start {
  align-self: flex-start;
}
</style>
