<script setup lang="ts">
import { ref, computed } from 'vue';
import { debounce } from 'quasar';
import VueMarkdown from 'vue-markdown-render';
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();
const changeLogText = ref('');
fetch(window.location.origin + '/data/changelog.md')
  .then((response) => {
    return response.text();
  })
  .then(function (data) {
    console.log(data); // this will be a string
    changeLogText.value = data;
  });

const dataColumnExplanations = [
  { name: 'Title', explanation: 'The title of the paper in plain text.' },
  {
    name: 'AuthorNames-Deduped',
    explanation:
      'The authors of the paper in the same order as the paper, separated by semicolon. Names are deduplicated with the same convention as dblp.',
  },
  { name: 'Abstract', explanation: 'The abstract of the paper.' },
  { name: 'DOI', explanation: 'The DOI of the paper.' },
  {
    name: 'Venue',
    explanation:
      'The venue of the paper. [vis, InfoVis, SciVis, VAST, CHI, or EuroVis]',
  },
  {
    name: 'Year',
    explanation:
      'The year the paper was published, not to be confused with the year the paper was presented.',
  },
  {
    name: 'Award',
    explanation:
      'The awards the paper received, separated by semicolon. Past records for these are unreliable, so these are incomplete. TT: Test of Time, BP: Best Paper, HM: Honorable Mention, BA: Best Application, BCS: Best Case Study.',
  },
  {
    name: 'Resources',
    explanation:
      'A list of resource keys, separated by semicolon. Examples of resource types are listed below.',
  },
];

const resourceExplanations = [
  {
    icon: 'paper',
    name: 'Paper Preprint (V)',
    explanation:
      'A version of the paper that is nearly identical to the final version, but not formatted by the publisher. This version is usually hosted on a preprint server and is always free to access.',
  },
  {
    icon: 'video',
    name: 'Fast Forward (V)',
    explanation:
      'A short 30 second video that summarizes the main idea of the paper.',
  },
  {
    icon: 'video',
    name: 'Prerecorded Talk (V)',
    explanation:
      'A precorded version of the talk that was given at the conference',
  },
  {
    icon: 'project_website',
    name: 'Project Website (PW)',
    explanation:
      'A landing page for the project that the paper is about. This often contains other resources such as videos, demos, and source code.',
  },
  {
    icon: 'code',
    name: 'Source Code (C)',
    explanation: 'The source code for the software that the paper is about.',
  },
  {
    icon: 'code',
    name: 'Analysis Code (C)',
    explanation:
      'Data analysis code used to generate the results in the paper.',
  },
  {
    icon: 'data',
    name: 'Data (D)',
    explanation: 'Data collected or presented in the paper.',
  },
  {
    icon: 'other',
    name: 'Other (O)',
    explanation: 'Presentation slides, blog posts, podcasts, etc.',
  },
];

const bibTexString = `@preprint{2024_preprint_vispubs,
  title = {VisPubs.com: A Visualization Publications Repository},
  author = {Devin Lange},
  booktitle = {Preprint},
  doi = {10.31219/osf.io/dg3p2},
  year = {2024}
}`;


const clipboardSupported = computed(() => {
  return navigator.clipboard && navigator.clipboard.writeText;
});

function copyCitationInfo() {
  navigator.clipboard.writeText(bibTexString);
  showCopiedToClipboardMessage.value = true;
  hideCopiedToClipboardMessageDebounced();
}
const hideCopiedToClipboardMessageDebounced = debounce(
  hideCopiedToClipboardMessage,
  1500
);

function hideCopiedToClipboardMessage() {
  showCopiedToClipboardMessage.value = false;
}

const showCopiedToClipboardMessage = ref(false);

const datasetComparisonRows = ref([
  {
    name: 'IEEE VIS',
    vispubdata: '✅',
    vispubs: '✅',
  },
  {
    name: 'Title, Authors, Abstract, DOI, Venue, Year, Award',
    vispubdata: '✅',
    vispubs: '✅',
  },
  {
    name: 'Citations, Internal References, Author Affiliations, Author Keywords, First/Last Page',
    vispubdata: '✅',
    vispubs: '',
  },
  {
    name: 'EuroVis, CHI',
    vispubdata: '',
    vispubs: '✅',
  },

  {
    name: 'Paper Resource Links (Preprint, Code, Data, ...)',
    vispubdata: '',
    vispubs: '✅',
  },
]);
const datasetComparisonColumns = ref([
  {
    name: 'name',
    label: '',
    align: 'left',
    field: 'name',
  },
  {
    name: 'vispubdata',
    label: 'Vispubdata',
    align: 'center',
    field: 'vispubdata',
  },
  {
    name: 'vispubs',
    label: 'VisPubs',
    align: 'center',
    field: 'vispubs',
  },
]);
</script>

<template>
  <q-page-container>
    <q-page>
      <div class="flex justify-center outer-container text-body1">
        <div class="q-pa-lg text-container">
          <p>
            VisPubs was created by
            <a href="https://www.devinlange.com/"
              >Devin Lange <q-icon name="open_in_new"
            /></a>
            to aggregate visualization publications from multiple venues (VIS,
            EuroVis, CHI) into a single website, and make it easy to find
            resources related to publications.
          </p>

          <div class="fancy-header q-pa-sm q-pr-lg text-h4 q-mb-md q-mt-sm">
            Citation Information
          </div>
          <p>
            I have written a short paper with more information about data
            aquisition, data format, and the website. A
            <a href="https://osf.io/preprints/osf/dg3p2">
              preprint of this short paper <q-icon name="open_in_new"
            /></a>
            is available on OSF. If you use the data or find the website to be
            useful, please cite this paper.
          </p>

          <q-card
            flat
            bordered
            class="q-mb-md"
            :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-2'"
          >
            <q-card-section>
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h6">BibTeX</div>
                </div>

                <div class="col-auto">
                  <Transition>
                    <q-badge v-if="showCopiedToClipboardMessage"
                      >Copied to clipboard</q-badge
                    >
                  </Transition>
                  <q-btn
                  v-if="clipboardSupported"
                    round
                    flat
                    icon="content_copy"
                    title="Copy BibTeX to Clipboard"
                    @click="copyCitationInfo"
                  />
                </div>
              </div>
              <pre>{{ bibTexString }}</pre>
            </q-card-section>
          </q-card>

          <div class="fancy-header q-pa-sm q-pr-lg text-h4 q-mb-md q-mt-sm">Data Format</div>
          <p>
            Currently this site includes IEEE Visualization (<b>VIS</b>)
            publications from 1990–2023, <b>EuroVis</b> publications from
            1999–2023, and <b>CHI</b> publications from 1986–2023.

            To download a <i>static</i> version of the full dataset, select the EXPORT button without any filters or
            search term.

            You can also access a <i>live</i> version of the dataset from <a href="https://vispubs.com/data/papers.csv">vispubs.com/data/papers.csv</a>.

          </p>
          <p>
            If you notice a mistake, or would like to make a
            suggestion, please
            <a href="https://github.com/Dev-Lan/vispubs/issues"
              >submit a new issue <q-icon name="open_in_new" /></a
            >.
          </p>
          <div class="fancy-subheader text-h5 q-mb-sm">
            How is this different from the Visualization Publication Dataset?
          </div>
          <p>
            The
            <a href="https://sites.google.com/site/vispubdata/home"
              >Visualization Publications Dataset <q-icon name="open_in_new"
            /></a>
            is an amazing resource that made this website possible. The main
            difference is that Visualization Publications Dataset
            (<b>Vispubdata</b>) contains more metadata about each paper, but
            this dataset (<b>VisPubs</b>) contains more papers, and includes
            resources related to papers.
          </p>
          <q-table
            wrap-cells
            class="q-mb-md"
            :rows="datasetComparisonRows"
            :columns="datasetComparisonColumns"
            row-key="name"
            hide-bottom
            flat
            bordered
          />
          <div class="fancy-subheader text-h5 ">Data Columns</div>
          <q-list class="q-mb-md">
            <q-item
              v-for="dataColumnExplanation in dataColumnExplanations"
              :key="dataColumnExplanation.name"
            >
              <q-item-section>
                <q-item-label>{{ dataColumnExplanation.name }}</q-item-label>
                <q-item-label caption>{{
                  dataColumnExplanation.explanation
                }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
          <div class="fancy-subheader text-h5 q-mb-sm">Publication Resources</div>
          <p>
            These resources can be anything to help explain the paper, use the
            related tool, or reproduce the results. Common types of resources
            include:
          </p>
          <q-list class="q-mb-md">
            <q-item
              v-for="resourceExplanation in resourceExplanations"
              :key="resourceExplanation.icon"
            >
              <q-item-section avatar>
                <q-avatar
                  :color="
                    paperDataStore.getResourceColor(resourceExplanation.icon)
                  "
                  :text-color="
                    paperDataStore.getResourceTextColor(
                      resourceExplanation.icon
                    )
                  "
                  :icon="
                    paperDataStore.getResourceIcon(resourceExplanation.icon)
                  "
                  size="md"
                />
              </q-item-section>

              <q-item-section>
                <q-item-label>{{ resourceExplanation.name }}</q-item-label>
                <q-item-label caption>{{
                  resourceExplanation.explanation
                }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>

          <p>
            Some resources have been added in bulk for all papers, however, the
            linked resources are not exhaustive. To add additional links for a
            paper navigate to it's page and click the
            <q-avatar
              class="q-ml-sm"
              color="primary"
              text-color="white"
              icon="add"
              size="xs"
            />
            <span class="q-ml-sm q-mr-sm">Add Resources</span> button.
          </p>

          <div class="fancy-subheader text-h5 q-mb-sm">Filtering CHI Papers</div>
          <p>
            VisPubs does not include every paper from CHI. Instead it attempts
            to select "visualization" papers. Papers that include at least one
            of the following keywords in the title or abstract are included.
            <ul>
              <li>"visualization", "visualisation"</li>
              <li>"visualizing", "visualising"</li>
              <li>"visual analytics", "visual analysis", "visual analyses"</li>
              <li>"visual data"</li>
              <li>"physical data", "data physical"</li>
            </ul>
          </p>
          <div class="fancy-header q-pa-sm q-pr-lg text-h4">
            Dataset Changelog
          </div>
          <vue-markdown :source="changeLogText" />
        </div>
      </div>
    </q-page>
  </q-page-container>
</template>

<style lang="scss">
.text-container {
  max-width: 750px;
}

.body--light .outer-container {
  background-color: $grey-2;
}

.body--light .text-container {
  background-color: white;
}

.body--dark .outer-container {
  background-color: $grey-10;
}

.body--dark .text-container {
  background-color: black;
}

.fancy-header {
  // outline: 5px solid $primary;
  background: $primary;
  color: white;
  display: inline-block;
  // circular border on right side
  border-top-right-radius: 1em;
  border-bottom-right-radius: 1em;
  // slight roundness on left side
  border-top-left-radius: 0.1em;
  border-bottom-left-radius: 0.1em;
}

.fancy-subheader {
  // outline: 1px solid $primary;
}

h4,
h5,
h6 {
  margin-top: 1em;
  margin-bottom: 1em;
}

a {
  color: $primary;
}

.v-enter-active,
.v-leave-active {
  transition: opacity 0.25s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}

pre {
  white-space: pre-wrap;
}
</style>
