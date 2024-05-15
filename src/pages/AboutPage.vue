<script setup lang="ts">
import { ref } from 'vue';
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

const resourceExplanations = [
  {
    icon: 'paper',
    name: 'Paper Preprint',
    explanation:
      'A version of the paper that is nearly identical to the final version, but not formatted by the publisher. This version is usually hosted on a preprint server and is always free to access.',
  },
  {
    icon: 'video',
    name: 'Fast Forward',
    explanation:
      'A short 30 second video that summarizes the main idea of the paper.',
  },
  {
    icon: 'video',
    name: 'Prerecorded Talk',
    explanation:
      'A precorded version of the talk that was given at the conference',
  },
  {
    icon: 'project_website',
    name: 'Project Website',
    explanation:
      'A landing page for the project that the paper is about. This often contains other resources such as videos, demos, and source code.',
  },
  {
    icon: 'code',
    name: 'Source Code',
    explanation: 'The source code for the software that the paper is about.',
  },
  {
    icon: 'code',
    name: 'Analysis Code',
    explanation:
      'Data analysis code used to generate the results in the paper.',
  },
  {
    icon: 'data',
    name: 'Data',
    explanation: 'Data collected or presented in the paper.',
  },
  {
    icon: 'other',
    name: 'Other',
    explanation: 'Presentation slides, blog posts, podcasts, etc.',
  },
];
</script>

<template>
  <q-page-container>
    <q-page>
      <div class="flex justify-center outer-container">
        <div class="q-pa-lg text-container">
          <p>
            Vispubs was created by
            <a href="https://www.devinlange.com/"
              >Devin Lange <q-icon name="open_in_new"
            /></a>
            to aggregate visualization publications from multiple venues (VIS,
            EuroVis, CHI) into a single website, and make it easy to find
            resources related to publications.
          </p>

          <div class="fancy-header q-pa-sm q-pr-lg text-h4">
            Citation Information
          </div>
          <p>https://osf.io/preprints/osf/dg3p2</p>
          <p>button to download</p>
          <div class="fancy-header q-pa-sm q-pr-lg text-h4">Data Format</div>
          <p>todo, content</p>

          <div class="fancy-subheader text-h5">Data Columns</div>
          <p>todo, content</p>

          <div class="fancy-subheader text-h5">Data Collection</div>
          filtering CHI / papers, other brief explanation for collection
          <div class="fancy-subheader text-h5">Publication Resources</div>
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

          <p>
            Currently this site includes IEEE Visualization (<b>VIS</b>)
            publications from 1990–2023, <b>EuroVis</b> publications from
            1999–2023, and <b>CHI</b> publications from 1986–2023. The VIS
            papers are based on a subset of data from this
            <a href="https://sites.google.com/site/vispubdata/home"
              >visualization publication dataset
              <q-icon name="open_in_new" /></a
            >. Thank you to all the creators/maintainers of this dataset!
          </p>
          <p>
            If you notice any mistakes, or would like to make a suggestion,
            please
            <a href="https://github.com/Dev-Lan/vispubs/issues"
              >let me know<q-icon name="open_in_new" /></a
            >.
          </p>
          <div class="fancy-subheader text-h5">
            How is this different from the Visualization Publication Dataset?
          </div>
          <p>todo, content</p>

          <div class="fancy-header q-pa-sm q-pr-lg text-h4">RegEx Tips</div>
          <p>todo, content</p>

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
  // outline: solid red 4px;
  max-width: 750px;
  margin-left: auto;
  margin-right: auto;
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
  font-size: 1.1em;
}
</style>
