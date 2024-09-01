<script setup lang="ts">
import { computed, ref } from 'vue';
import { usePaperDataStore } from 'src/stores/paperDataStore';
import { useAuthorStore } from 'src/stores/authorStore';
import Highlighter from 'vue-highlight-words';
import { useQuasar } from 'quasar';

const $q = useQuasar();
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

const addResourcesShown = ref(false);

interface LabeledLink {
  label: string;
  url: string;
  external: boolean;
}

interface AuthorLink extends LabeledLink {
  allAuthors?: boolean;
}
const authorSearchOptions: AuthorLink[] = [
  {
    label: 'This site',
    url: './?searchText=',
    external: false,
  },
  {
    label: 'This site (all authors)',
    url: './?useRegex=true&searchText=',
    external: false,
    allAuthors: true,
  },
  {
    label: 'Google Scholar',
    url: 'https://scholar.google.com/scholar?q=',
    external: true,
  },
  {
    label: 'Google',
    url: 'https://www.google.com/search?q=',
    external: true,
  },
  {
    label: 'Bing',
    url: 'https://www.bing.com/search?q=',
    external: true,
  },
  {
    label: 'DuckDuckGo',
    url: 'https://www.duckduckgo.com/?q=',
    external: true,
  },
];

const paperSearchOptions: LabeledLink[] = [
  {
    label: 'Google Scholar',
    url: 'https://scholar.google.com/scholar?q=',
    external: true,
  },
  {
    label: 'Google',
    url: 'https://www.google.com/search?q=',
    external: true,
  },
  {
    label: 'Bing',
    url: 'https://www.bing.com/search?q=',
    external: true,
  },
  {
    label: 'DuckDuckGo',
    url: 'https://www.duckduckgo.com/?q=',
    external: true,
  },
];

function quoted(text: string): string {
  return `"${text}"`;
}

function copyToClipboard(text: string): void {
  navigator.clipboard.writeText(text);
  $q.notify({
    message: `Copied "${text}" to clipboard.`,
    position: 'bottom',
    icon: 'content_copy',
    timeout: 2500,
  });
}

const clipboardSupported = computed(() => {
  return navigator.clipboard && navigator.clipboard.writeText;
});

const authors = computed(() =>
  paperDataStore.getAuthors(paperDataStore.selectedPaper)
);

const allAuthorsQuery = computed(() => {
  return authors.value
    .map((author) => author.displayName)
    .reduce((x, y) => x + '|' + y);
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

    <q-btn
      class="q-mr-md"
      padding="sm"
      color="primary"
      size="sm"
      push
      icon="casino"
      title="Get Random Paper"
      :disable="!paperDataStore.papers || paperDataStore.papers.length === 0"
      @click="paperDataStore.selectRandomPaper"
    />

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
      <q-btn flat no-caps :size="$q.screen.gt.xs ? 'lg' : 'md'">
        <Highlighter
          highlightClassName="highlight"
          :searchWords="searchWords"
          :autoEscape="autoEscape"
          :caseSensitive="caseSensitive"
          :textToHighlight="paperDataStore.selectedPaper.title"
        />
        <q-menu touch-position>
          <q-list style="min-width: 100px">
            <q-item
              clickable
              :href="`https://doi.org/${paperDataStore.selectedPaper.doi}`"
              target="_blank"
            >
              <q-item-section>Publication</q-item-section>
              <q-item-section avatar>
                <q-avatar size="sm" icon="open_in_new" />
              </q-item-section>
            </q-item>
            <q-separator />
            <q-item dense>
              <q-item-section class="text-caption">Search:</q-item-section>
            </q-item>
            <template v-for="option in paperSearchOptions" :key="option.label">
              <q-item
                clickable
                dense
                :href="option.url + quoted(paperDataStore.selectedPaper.title)"
                :target="option.external ? '_blank' : ''"
              >
                <q-item-section>
                  {{ option.label }}
                </q-item-section>
                <q-item-section avatar v-if="option.external">
                  <q-avatar size="sm" icon="open_in_new" />
                </q-item-section>
              </q-item>
            </template>
            <q-item
              v-if="clipboardSupported"
              clickable
              dense
              v-close-popup
              @click="copyToClipboard(paperDataStore.selectedPaper.title)"
            >
              <q-item-section>Copy Title</q-item-section>
              <q-item-section avatar>
                <q-avatar size="sm" icon="content_copy" />
              </q-item-section>
            </q-item>

            <q-item
              v-if="clipboardSupported"
              clickable
              dense
              v-close-popup
              @click="copyToClipboard(paperDataStore.selectedPaper.doi)"
            >
              <q-item-section>Copy DOI</q-item-section>
              <q-item-section avatar>
                <q-avatar size="sm" icon="content_copy" />
              </q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
    </div>
    <div class="q-mb-sm q-mx-sm flex justify-center items-center">
      <div :class="$q.screen.gt.xs ? 'text-body2' : 'text-caption'">
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
        v-for="({ displayName, dedupedName }, index) in authors"
        :key="index"
      >
        <q-btn flat no-caps :size="$q.screen.gt.xs ? 'md' : 'sm'">
          <template:label>
            <Highlighter
              highlightClassName="highlight"
              :searchWords="searchWords"
              :autoEscape="autoEscape"
              :textToHighlight="displayName"
            />
          </template:label>
          <q-menu>
            <q-list style="min-width: 100px">
              <template v-if="authorHasWebsite(dedupedName)">
                <q-item
                  clickable
                  :href="getAuthorWebsite(dedupedName)"
                  target="_blank"
                >
                  <q-item-section>Homepage</q-item-section>
                  <q-item-section avatar>
                    <q-avatar size="sm" icon="open_in_new" />
                  </q-item-section>
                </q-item>
                <q-separator />
              </template>
              <q-item dense>
                <q-item-section class="text-caption">Search:</q-item-section>
              </q-item>
              <template
                v-for="option in authorSearchOptions"
                :key="option.label"
              >
                <q-item
                  clickable
                  dense
                  :href="
                    option.allAuthors
                      ? option.url + allAuthorsQuery
                      : option.url + displayName
                  "
                  :target="option.external ? '_blank' : ''"
                >
                  <q-item-section>
                    {{ option.label }}
                  </q-item-section>
                  <q-item-section avatar v-if="option.external">
                    <q-avatar size="sm" icon="open_in_new" />
                  </q-item-section>
                </q-item>
              </template>
              <q-item
                v-if="clipboardSupported"
                clickable
                dense
                v-close-popup
                @click="copyToClipboard(displayName)"
              >
                <q-item-section>Copy Author</q-item-section>
                <q-item-section avatar>
                  <q-avatar size="sm" icon="content_copy" />
                </q-item-section>
              </q-item>
              <template v-if="!authorHasWebsite(dedupedName)">
                <q-separator />
                <q-item dense>
                  <q-item-section class="text-caption"
                    >Submit Homepage:</q-item-section
                  >
                </q-item>
                <q-item
                  dense
                  clickable
                  :href="getAuthorFormLink(dedupedName)"
                  target="_blank"
                >
                  <q-item-section>Google Form</q-item-section>
                  <q-item-section avatar>
                    <q-avatar size="sm" icon="open_in_new" />
                  </q-item-section>
                </q-item>
              </template>
            </q-list>
          </q-menu>
        </q-btn>
      </template>
    </div>
    <div class="flex flex-center reverse-wrap">
      <q-card flat bordered class="q-ml-md q-mr-md q-mb-md self-end">
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

            <q-separator
              v-if="paperDataStore.selectedPaperResourceLinks.length > 0"
              class="q-mt-md q-mb-md"
            />

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
      <div class="mw-600 q-mb-lg self-end text-body1">
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
