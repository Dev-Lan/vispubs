<script setup lang="ts">
import { ref } from 'vue';
import VueMarkdown from 'vue-markdown-render';
const changeLogText = ref('');
fetch(window.location.origin + '/data/changelog.md')
  .then((response) => {
    return response.text();
  })
  .then(function (data) {
    console.log(data); // this will be a string
    changeLogText.value = data;
  });
</script>

<template>
  <q-page-container>
    <q-page>
      <div class="q-ma-lg">
        <p>
          This website is a personal project to create a single website that
          contains all visualization publications. Currently this site includes
          IEEE Visualization (IEEE VIS) publications from 1990–2022 and EuroVis
          publications from 1999–2023. The VIS papers are based on a subset of
          data from this
          <a href="https://sites.google.com/site/vispubdata/home?authuser=0"
            >visualization publication dataset</a
          >. Thank you to all the creators/maintainers of this dataset!
        </p>
        <p>
          In addition to publications, I would like to facilite finding
          resources related to the publication. This includes link to authors
          research page. If you would like to suggest a website for an author,
          fill out
          <a href="https://forms.gle/WuXG2ZSidd9A9Ns57">this form</a>. The
          change will be active on the website the next time I push an update.
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
