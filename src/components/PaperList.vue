<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import Highlighter from 'vue-highlight-words';
import { usePaperDataStore } from 'src/stores/paperDataStore';
import { unparse } from 'papaparse';
import { saveAs } from 'file-saver';
import ExcelJS from 'exceljs';
import { storeToRefs } from 'pinia';
import SimpleBar from './SimpleBar.vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();
const paperDataStore = usePaperDataStore();
const { selectedPaperIndex, focusedPaperIndex } = storeToRefs(paperDataStore);

const caseSensitive = computed(() => {
  return paperDataStore.matchCase ? true : false;
});
const autoEscape = computed(() => {
  return paperDataStore.useRegex ? false : true;
});

const searchWords = computed(() => {
  return [paperDataStore.searchText];
});

const clipboardSupported = computed(() => {
  return navigator.clipboard && navigator.clipboard.writeText;
});

function exportToJSON() {
  const json = JSON.stringify(paperDataStore.papersWithLinks);
  const blob = new Blob([json], { type: 'application/json' });
  saveAs(blob, 'vispubs.json');
}

function copyJSON() {
  const json = JSON.stringify(paperDataStore.papersWithLinks);
  copyToClipboard(json);
}

function exportToCSV() {
  const csv = unparse(paperDataStore.papersWithLinks);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, 'vispubs.csv');
}

function copyCSV() {
  const csv = unparse(paperDataStore.papersWithLinks);
  copyToClipboard(csv);
}

function copyToClipboard(text: string): void {
  navigator.clipboard.writeText(text);

  const maxLength = 100;
  const displayText =
    text.length < maxLength ? text : text.slice(0, maxLength - 3) + '...';

  $q.notify({
    message: `Copied "${displayText}" to clipboard.`,
    position: 'bottom',
    icon: 'content_copy',
    timeout: 2500,
  });
}

async function exportToXLSX() {
  const workbook = new ExcelJS.Workbook();
  const vispubs = workbook.addWorksheet('VisPubs');

  vispubs.columns = [
    { header: 'Link', key: 'Link', width: 4 },
    { header: 'DOI', key: 'DOI', width: 10 },
    { header: 'Conference', key: 'Conference', width: 10 },
    { header: 'Year', key: 'Year', width: 5 },
    { header: 'Award', key: 'Award', width: 6 },
    { header: 'Resources', key: 'Resources', width: 10 },
    { header: 'Title', key: 'Title', width: 25 },
    { header: 'AuthorNames-Dedpuped', key: 'AuthorNamesDedpuped', width: 40 },
    { header: 'Abstract', key: 'Abstract', width: 150 },
  ];
  for (let i = 0; i < paperDataStore.papersWithLinks.length; i++) {
    const paper = paperDataStore.papersWithLinks[i];
    vispubs.addRow({
      Link: paper.link,
      DOI: paper.doi,
      Conference: paper.conference,
      Year: paper.year,
      Title: paper.title,
      AuthorNamesDedpuped: paper.authorNamesDeduped,
      Award: paper.award,
      Resources: paper.resources,
      Abstract: paper.abstract,
    });
    const linkCell = vispubs.getCell(`A${i + 2}`);
    linkCell.value = {
      text: 'link',
      hyperlink: paper.link ?? '',
      tooltip: paper.link,
    };
    linkCell.font = {
      color: { argb: '000000FF' },
      underline: true,
    };
  }

  const metadata = workbook.addWorksheet('Metadata');
  metadata.getColumn('A').width = 20;
  metadata.getColumn('B').width = 100;
  const now = new Date();
  metadata.addRow(['Date Downloaded', now.toLocaleDateString()]);
  metadata.addRow(['Time Downloaded', now.toLocaleTimeString()]);
  metadata.addRow(['Timezone Offset', now.getTimezoneOffset() / 60]);
  metadata.addRow(['Search String', paperDataStore.searchText]);
  metadata.addRow(['Use Regex', paperDataStore.useRegex ? 'true' : 'false']);
  metadata.addRow(['Match Case', paperDataStore.matchCase ? 'true' : 'false']);
  metadata.addRow(['Link', window.location.href]);
  const linkCell = metadata.getCell('B7');
  linkCell.value = {
    text: window.location.href,
    hyperlink: window.location.href,
    tooltip: window.location.href,
  };
  linkCell.font = {
    color: { argb: '000000FF' },
    underline: true,
  };

  const buffer = await workbook.xlsx.writeBuffer();
  saveAs(
    new Blob([buffer], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }),
    'vispubs.xlsx'
  );
}

const searchbar = ref();
function clearSearchbar() {
  paperDataStore.searchText = '';
  // set focus back to searchbar
  if (searchbar.value) {
    searchbar.value.focus();
  }
}
const exportShown = ref(false);

const offset = 50 + 50; // height of header + inner toolbar

const virtualScrollRef = ref(null);
watch(selectedPaperIndex, () => {
  scrollToSelected();
});

watch(focusedPaperIndex, () => {
  scrollToFocused();
});

onMounted(() => {
  scrollToSelected();
});

function scrollToSelected() {
  if (selectedPaperIndex.value === null) {
    return;
  }
  scrollToPaper(selectedPaperIndex.value);
}

function scrollToFocused() {
  if (paperDataStore.focusedPaperIndex === null) {
    return;
  }
  scrollToPaper(paperDataStore.focusedPaperIndex);
}

function scrollToPaper(index: number): void {
  if (virtualScrollRef.value === null) {
    return;
  }
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  virtualScrollRef.value.scrollTo(index);
}

function onSearchbarFocus() {
  paperDataStore.searchFocused = true;
}

function onSearhbarBlur() {
  paperDataStore.searchFocused = false;
  paperDataStore.clearFocusedPaper();
}

const hoveredIndex = ref<number | null>();
</script>

<template>
  <q-toolbar>
    <!-- warning: if spacing is changed, offset will have to change -->
    <q-btn
      class="q-mr-sm"
      padding="sm"
      color="primary"
      size="sm"
      push
      icon="filter_alt"
      @click="paperDataStore.filterPanelOpen = !paperDataStore.filterPanelOpen"
      :title="
        paperDataStore.filterPanelOpen
          ? 'Close Filter Panel'
          : 'Open Filter Panel'
      "
    />

    <q-input
      ref="searchbar"
      rounded
      outlined
      dense
      :class="`flex-grow-1 ${$q.screen.gt.xs ? 'q-mr-md' : 'q-mr-sm'}`"
      label="Search (Title, Author, Abstract)"
      v-model="paperDataStore.searchText"
      @keydown.enter="paperDataStore.selectFocusedPaper()"
      @focus="onSearchbarFocus"
      @blur="onSearhbarBlur"
    >
      <template v-slot:append>
        <q-btn-toggle
          v-model="paperDataStore.matchCase"
          bordered
          no-caps
          clearable
          toggle-color="primary"
          color="white"
          text-color="primary"
          dense
          size="sm"
          title="Match Case"
          :options="[{ label: 'Aa', value: 'true' }]"
        />

        <q-btn-toggle
          v-model="paperDataStore.useRegex"
          bordered
          no-caps
          clearable
          toggle-color="primary"
          color="white"
          text-color="primary"
          dense
          size="sm"
          title="Use Regex"
          :options="[{ label: '[.*]', value: 'true' }]"
        />
        <q-icon v-if="paperDataStore.searchText === ''" name="search" />
        <q-btn
          v-else
          icon="clear"
          flat
          round
          title="Clear search text"
          dense
          style="margin-right: -9.6px"
          @click="clearSearchbar"
        />
        <!-- -9.6 is hack to get btn to match width of q-icon -->
      </template>
    </q-input>
    <q-btn
      class="gt-xs q-mr-md"
      padding="sm"
      color="primary"
      size="sm"
      push
      icon="casino"
      title="Get Random Paper"
      :disable="!paperDataStore.papers || paperDataStore.papers.length === 0"
      @click="paperDataStore.selectRandomPaper"
    />
    <div :class="`paper-count ${$q.screen.gt.xs ? 'q-mr-md' : 'q-mr-sm'}`">
      <span
        >{{ paperDataStore.papers.length
        }}{{ $q.screen.gt.xs ? ' papers' : '' }}</span
      >
      <SimpleBar
        v-if="paperDataStore.allData !== null"
        :count="paperDataStore.papers.length"
        :maxCount="paperDataStore.allData.length"
      />
    </div>
    <q-btn
      class=""
      color="primary"
      push
      size="sm"
      :disable="!paperDataStore.papers || paperDataStore.papers.length === 0"
      icon="file_download"
      title="Export selected papers"
      :round="!$q.screen.gt.xs"
      :label="$q.screen.gt.xs ? 'Export' : ''"
      @click="exportShown = true"
    />

    <q-dialog v-model="exportShown">
      <q-card>
        <q-card-section>
          <div class="text-h6">Export selected metadata as...</div>
        </q-card-section>

        <q-card-section class="q-pb-none flex column">
          <span class="q-mb-lg flex row justify-start items-center">
            <q-btn
              color="primary"
              push
              size="md"
              icon="file_download"
              label="EXCEL"
              title="download Excel file"
              @click="exportToXLSX"
            />
          </span>
          <span class="q-mb-lg flex row justify-start items-center">
            <q-btn
              class="q-mr-sm"
              color="primary"
              push
              size="md"
              icon="file_download"
              label="CSV"
              title="download csv file"
              @click="exportToCSV"
            />
            <q-btn
              v-if="clipboardSupported"
              size="md"
              icon="content_copy"
              label="copy"
              title="copy csv to clipboard"
              @click="copyCSV"
            />
          </span>
          <span class="q-mb-lg flex row justify-start items-center">
            <q-btn
              class="q-mr-sm"
              color="primary"
              push
              size="md"
              icon="file_download"
              label="JSON"
              title="download json file"
              @click="exportToJSON"
            />
            <q-btn
              v-if="clipboardSupported"
              size="md"
              icon="content_copy"
              label="copy"
              title="copy json to clipboard"
              @click="copyJSON"
            />
          </span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            label="Done"
            color="primary"
            v-close-popup
            title="Close Popup"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-toolbar>
  <q-virtual-scroll
    ref="virtualScrollRef"
    v-if="paperDataStore.papers.length > 0"
    :items="paperDataStore.papers"
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
      :manual-focus="paperDataStore.focusedPaperIndex !== null"
      :focused="
        index === paperDataStore.focusedPaperIndex || index === hoveredIndex
      "
      @focus="paperDataStore.focusPaper(index)"
      @mouseover="hoveredIndex = index"
      @mouseleave="hoveredIndex = null"
    >
      <q-item-section>
        <q-item-label>
          <Highlighter
            highlightClassName="highlight"
            :searchWords="searchWords"
            :autoEscape="autoEscape"
            :caseSensitive="caseSensitive"
            :textToHighlight="item.title"
          />
        </q-item-label>
        <q-item-label caption lines="2">
          <Highlighter
            highlightClassName="highlight"
            :searchWords="searchWords"
            :autoEscape="autoEscape"
            :caseSensitive="caseSensitive"
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
          ><span class="conference-year-label">{{
            `${paperDataStore.getConference(item)}, ${item.year}`
          }}</span>
          [{{ index + 1 }}]</q-item-label
        >
        <div class="flex items-center">
          <q-avatar
            v-if="item.accessible"
            color="primary"
            text-color="white"
            icon="accessibility_new"
            size="xs"
            class="q-mr-xs"
          />
          <q-avatar
            v-for="(resourceLink, index) in paperDataStore.getKeyList(
              item.resources
            )"
            :key="index"
            :color="paperDataStore.getResourceColor(resourceLink)"
            :text-color="paperDataStore.getResourceTextColor(resourceLink)"
            :icon="paperDataStore.getResourceIcon(resourceLink)"
            size="xs"
            class="q-mr-xs"
          />
          <q-badge
            v-for="(award, index) in paperDataStore.getKeyList(item.award)"
            :key="index"
            color="positive"
            outline
            class="q-ml-xs"
            ><span class="gt-xs">{{ paperDataStore.getAward(award) }}</span>
            <q-icon name="emoji_events" color="positive" size="xs" />
          </q-badge>
        </div>
      </q-item-section>
    </q-item>
  </q-virtual-scroll>
  <q-card v-else flat bordered square>
    <q-card-section>
      <div class="text-h6">No papers found...</div>

      <span v-if="paperDataStore.validRegex">
        with {{ paperDataStore.useRegex ? 'Regex ' : '' }}"{{
          paperDataStore.searchText
        }}" in the <b>Title</b>, <b>Author List</b>, or <b>Abstract</b>.
      </span>
      <q-banner rounded v-else inline-actions class="error-message">
        <div class="text-h6 text-negative">Error</div>
        <div class="text-dark">{{ paperDataStore.regexErrorString }}</div>
      </q-banner>
    </q-card-section>
  </q-card>
</template>

<style scoped lang="scss">
.flex-grow-1 {
  flex-grow: 1;
}

.error-message {
  border: solid $red-10 1px;
  background-color: $red-1;
}

.paper-count {
  width: 80px;
  @media (max-width: $breakpoint-xs-max) {
    width: 32px;
  }
}

.body--light .conference-year-label {
  color: black;
}

.body--dark .conference-year-label {
  color: white;
}
</style>
