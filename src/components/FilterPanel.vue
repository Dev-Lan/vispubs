<script setup lang="ts">
import { computed } from 'vue';

import FilterButton from 'src/components/FilterButton.vue';

import { scaleLinear } from 'd3-scale';

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

function closePanel() {
  paperDataStore.filterPanelOpen = false;
}
</script>

<template>
  <q-toolbar>
    <q-icon class="q-mr-sm" size="sm" name="filter_alt" />
    <span class="text-h5">Filter by...</span>
    <q-space />
    <q-btn round size="sm" icon="close" @click="closePanel" />
  </q-toolbar>
  <template v-if="paperDataStore.allData">
    <q-card flat>
      <q-card-section class="q-pb-none q-pt-none">
        <div class="text-h6">
          Year
          <q-btn
            v-if="paperDataStore.yearFilterSet"
            padding="xs"
            size="sm"
            flat
            no-caps
            @click="paperDataStore.clearYearFilter()"
            class="text-caption"
            >(clear filter)</q-btn
          >
        </div>
      </q-card-section>
      <q-card-section class="q-pt-xs q-pb-lg">
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
          dense
          label
          switch-label-side
          snap
          :style="`width: ${yearVisWidth}px;`"
        />
      </q-card-section>
    </q-card>

    <q-card flat>
      <q-card-section class="q-pb-none q-pt-none">
        <div class="text-h6">
          Venue
          <q-btn
            v-if="paperDataStore.venueFilter.size > 0"
            padding="xs"
            size="sm"
            flat
            no-caps
            @click="paperDataStore.clearVenueFilter()"
            class="text-caption"
            >(clear filter)</q-btn
          >
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none flex justify-between">
        <FilterButton
          v-for="venueCount in paperDataStore.venueCounts"
          :key="venueCount.venue"
          :text="venueCount.venue"
          :count="venueCount.count"
          :maxCount="paperDataStore.maxVenueCount"
          :selected="paperDataStore.venueFilter.has(venueCount.venue)"
          @click="paperDataStore.toggleVenueFilter(venueCount.venue)"
        />
      </q-card-section>
    </q-card>

    <q-card flat>
      <q-card-section class="q-pb-none q-pt-none">
        <div class="text-h6">
          Awards
          <q-btn
            v-if="paperDataStore.awardFilter.size > 0"
            padding="xs"
            size="sm"
            flat
            no-caps
            class="text-caption"
            @click="paperDataStore.clearAwardFilter()"
            >(clear filter)</q-btn
          >
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none">
        <FilterButton
          v-for="awardCount in paperDataStore.awardCounts"
          :key="awardCount.award"
          :text="awardCount.award"
          :count="awardCount.count"
          :maxCount="paperDataStore.maxAwardCount"
          :selected="paperDataStore.awardFilter.has(awardCount.award)"
          :width="100"
          @click="paperDataStore.toggleAwardFilter(awardCount.award)"
      /></q-card-section>
    </q-card>

    <q-card flat>
      <q-card-section class="q-pb-none q-pt-none">
        <div class="text-h6">
          Resources
          <q-btn
            v-if="paperDataStore.resourceFilter.size > 0"
            padding="xs"
            size="sm"
            flat
            no-caps
            class="text-caption"
            @click="paperDataStore.clearResourceFilter()"
            >(clear filter)</q-btn
          >
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none flex justify-between">
        <FilterButton
          v-for="resourceCount in paperDataStore.resourceCounts"
          :key="resourceCount.resource"
          :text="resourceCount.resource"
          :count="resourceCount.count"
          :maxCount="paperDataStore.maxResourceCount"
          :selected="paperDataStore.resourceFilter.has(resourceCount.resource)"
          :icon="resourceCount.key"
          @click="paperDataStore.toggleResourceFilter(resourceCount.resource)"
        />
      </q-card-section>
    </q-card>
  </template>
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
