<script setup lang="ts">
import { computed, ref } from 'vue';
import Highlighter from 'vue-highlight-words';
import { usePaperDataStore } from 'src/stores/paperDataStore';
import { unparse } from 'papaparse';
import { saveAs } from 'file-saver';
import ExcelJS from 'exceljs';

const paperDataStore = usePaperDataStore();

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
  navigator.clipboard.writeText(json);
}

function exportToCSV() {
  const csv = unparse(paperDataStore.papersWithLinks);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, 'vispubs.csv');
}

function copyCSV() {
  const csv = unparse(paperDataStore.papersWithLinks);
  navigator.clipboard.writeText(csv);
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

function getResourceKeys(string?: string): string[] {
  if (!string) {
    return [];
  }
  return string.split(';');
}

const exportShown = ref(false);

const offset = 50 + 50; // height of header + inner toolbar
</script>

<template>
  <q-toolbar>
    <!-- warning: if spacing is changed, offset will have to change -->
    <q-input
      ref="searchbar"
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

    <q-badge color="primary" outline class="q-mr-md"
      >{{ paperDataStore.papers.length }} papers</q-badge
    >

    <q-btn
      class="xs"
      color="primary"
      push
      size="sm"
      round
      :disable="!paperDataStore.papers || paperDataStore.papers.length === 0"
      icon="file_download"
      title="Export selected papers"
      @click="exportShown = true"
    />
    <q-btn
      class="gt-xs"
      color="primary"
      push
      size="sm"
      :disable="!paperDataStore.papers || paperDataStore.papers.length === 0"
      icon="file_download"
      title="Export selected papers"
      label="Export"
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
          <q-btn flat label="Done" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
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
          ><span style="color: black">{{
            `${paperDataStore.getConference(item)}, ${item.year}`
          }}</span>
          [{{ index + 1 }}]</q-item-label
        >
        <div class="flex items-center">
          <q-avatar
            v-for="(resourceLink, index) in getResourceKeys(item.resources)"
            :key="index"
            :color="paperDataStore.getResourceColor(resourceLink)"
            :text-color="paperDataStore.getResourceTextColor(resourceLink)"
            :icon="paperDataStore.getResourceIcon(resourceLink)"
            size="xs"
            class="q-mr-xs"
          />
          <q-badge v-if="item.award" color="positive" outline
            >{{ paperDataStore.getAward(item) }}
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
        <div>{{ paperDataStore.regexErrorString }}</div>
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
</style>
