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
      <div class="q-ma-lg">
        <p>
          Vispubs was created by
          <a href="https://www.devinlange.com/">Devin Lange</a> to aggregate all
          visualization publications into a single website, and make it easy to
          find resources related to publications. These resources can be
          anything to help explain the paper, use to related tool, or reproduce
          the results. Common types of resources include:
        </p>
        <q-list>
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
                  paperDataStore.getResourceTextColor(resourceExplanation.icon)
                "
                :icon="paperDataStore.getResourceIcon(resourceExplanation.icon)"
                size="md"
              />
            </q-item-section>

            <!-- <q-item-section>{{ resourceExplanation.name }}</q-item-section> -->
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
          paper navigate it's page and click the
          <q-avatar color="primary" text-color="white" icon="add" size="xs" />
          Add Resources button.
        </p>

        <p>
          Currently this site includes IEEE Visualization (IEEE VIS)
          publications from 1990–2023 and EuroVis publications from 1999–2023.
          The VIS papers are based on a subset of data from this
          <a href="https://sites.google.com/site/vispubdata/home?authuser=0"
            >visualization publication dataset</a
          >. Thank you to all the creators/maintainers of this dataset!
        </p>
        <p>
          If you notice any mistakes, or would like to make a suggestion, please
          <a href="https://github.com/Dev-Lan/vispubs/issues"
            >let me know here.</a
          >
        </p>
        <vue-markdown :source="changeLogText" />
      </div>
    </q-page>
  </q-page-container>
</template>

<style>
h4,
h5,
h6 {
  margin-top: 1em;
  margin-bottom: 1em;
}
</style>
