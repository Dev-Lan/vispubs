<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';

import { scaleLinear } from 'd3-scale';

import { useGlobalStore } from 'src/stores/globalStore';
const globalStore = useGlobalStore();

import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();

const yearVisHeight = 40;
const yearVisWidth = 240;
const rightLabelWidth = 20;
const betweenBarsPadding = 3;
const barWidth = computed(() => {
  if (paperDataStore.yearExtent === null) {
    return 0;
  }
  const numBars =
    paperDataStore.yearExtent[1] - paperDataStore.yearExtent[0] + 1;
  return (yearVisWidth - (numBars - 1) * betweenBarsPadding) / numBars;
});
const scaleHeight = computed(() => {
  return scaleLinear()
    .domain([0, paperDataStore.maxPapersInYear])
    .range([0, yearVisHeight]);
});

const scaleX = computed(() => {
  if (paperDataStore.yearExtent === null) {
    return () => 0;
  }
  return scaleLinear()
    .domain(paperDataStore.yearExtent)
    .range([0, yearVisWidth - barWidth.value]);
});
</script>

<template>
  <q-toolbar>
    <q-icon class="q-mr-sm" size="sm" name="filter_alt" />
    <span class="text-h5">Filter by...</span>
    <q-space />
    <q-btn
      round
      size="sm"
      icon="close"
      @click="globalStore.filterPanelOpen = false"
    />
  </q-toolbar>

  <!-- <div>{{ paperDataStore.yearExtent }}</div> -->
  <q-card flat>
    <q-card-section>
      <div class="text-h6">
        Year
        <q-btn
          v-if="paperDataStore.yearFilterSet"
          padding="xs"
          size="sm"
          flat
          no-caps
          @click="paperDataStore.clearYearFilter()"
          >(clear filter)</q-btn
        >
      </div>
    </q-card-section>
    <q-card-section>
      <svg :width="yearVisWidth + rightLabelWidth" :height="yearVisHeight">
        <g v-if="paperDataStore.papers.length > 0" class="right-label">
          <line x1="0" :x2="yearVisWidth + 2" y1="0" y2="0" />
          <text :x="yearVisWidth + 4" y="0" alignment-baseline="middle">
            {{ paperDataStore.maxPapersInYear }}
          </text>
        </g>
        <g v-else>
          <text
            :x="yearVisWidth / 2"
            :y="yearVisHeight / 2"
            alignment-baseline="middle"
            text-anchor="middle"
          >
            No papers
          </text>
        </g>
        <g class="bars">
          <rect
            v-for="yearCount in paperDataStore.paperYearCounts"
            :key="yearCount.year"
            :x="scaleX(yearCount.year)"
            :y="yearVisHeight - scaleHeight(yearCount.count)"
            :width="barWidth"
            :height="scaleHeight(yearCount.count)"
          />
        </g>
      </svg>
      <q-range
        v-if="paperDataStore.yearExtent !== null"
        v-model="paperDataStore.yearFilter"
        :min="paperDataStore.yearExtent[0]"
        :max="paperDataStore.yearExtent[1]"
        :step="1"
        drag-range
        dense
        label
        switch-label-side
        snap
        :style="`width: ${yearVisWidth}px;`"
      />
    </q-card-section>
  </q-card>

  <q-card flat>
    <q-card-section>
      <div class="text-h6">
        Venue <q-btn padding="xs" size="sm" flat no-caps>(clear filter)</q-btn>
      </div>
    </q-card-section>
    <q-card-section> TODO </q-card-section>
  </q-card>

  <q-card flat>
    <q-card-section>
      <div class="text-h6">
        Awards <q-btn padding="xs" size="sm" flat no-caps>(clear filter)</q-btn>
      </div>
    </q-card-section>
    <q-card-section> TODO </q-card-section>
  </q-card>

  <q-card flat>
    <q-card-section>
      <div class="text-h6">
        Resources
        <q-btn padding="xs" size="sm" flat no-caps>(clear filter)</q-btn>
      </div>
    </q-card-section>
    <q-card-section> TODO </q-card-section>
  </q-card>
</template>

<style scoped lang="scss">
svg {
  overflow: visible;
  //   background-color: bisque;
  //   outline: solid tomato 0px;
}

.bars {
  fill: $primary;
}

line {
  stroke: rgb(125, 125, 125);
  stroke-width: 0.5px;
}

text {
  font-size: 10pt;
  fill: rgb(125, 125, 125);
}
</style>
