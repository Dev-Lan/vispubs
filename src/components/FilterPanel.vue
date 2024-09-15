<script setup lang="ts">
import { ref, computed, watch } from 'vue';

import FilterButton from 'src/components/FilterButton.vue';

import { scaleLinear } from 'd3-scale';

import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();

const yearVisHeight = 40;
const yearVisWidth = 250;
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
    .domain([0, paperDataStore.maxPapersInYear.count])
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

const barChartLabelX = computed(() => {
  return scaleX.value(paperDataStore.maxPapersInYear.year) + barWidth.value / 2;
});

const selectedYear = ref<number | null>(null);
const selectedYearLabel = ref<string>('');
const totalSelectedPapers = ref<number>(0);
const selectedPapersByVenue = ref<Map<string, number>>(new Map());

const svgContainer = ref<SVGElement | null>(null);
function mouseMoveInSvg(event: PointerEvent) {
  if (!svgContainer.value) {
    return;
  }
  if (event.pointerType !== 'mouse') {
    return;
  }
  const svgRect = svgContainer.value.getBoundingClientRect();
  const x = event.clientX - svgRect.left;
  const year = Math.floor(scaleX.value.invert(x));
  selectedYear.value = year;
  selectedYearLabel.value = year.toString();
  const count = paperDataStore.paperYearCounts.find(
    (yearCount) => yearCount.year === year
  )?.count;
  totalSelectedPapers.value = count ?? 0;
  const papersInYear = paperDataStore.papers.filter(
    (paper) => paper.year === year
  );
  const venueCounts = new Map<string, number>();
  for (const paper of papersInYear) {
    const count = venueCounts.get(paper.conference) ?? 0;
    venueCounts.set(paper.conference, count + 1);
  }
  selectedPapersByVenue.value = venueCounts;
}

function mouseOutSvg(event: PointerEvent) {
  if (event.pointerType !== 'mouse') {
    return;
  }
  selectedYear.value = null;
  // do NOT reset the label, as it will still be used to display the tooltip
}

function clickInSvg() {
  if (selectedYear.value === null) {
    return;
  }
  paperDataStore.yearFilter = {
    min: selectedYear.value,
    max: selectedYear.value,
  };
}

const collectionKeyOptions = ['example', 'EuroVisSTAR'];
const collectionKeyMirror = ref<string | null>(paperDataStore.collectionKey);
watch(collectionKeyMirror, (newValue: string | null) => {
  if (newValue === null) {
    paperDataStore.clearCollectionKey();
  } else {
    paperDataStore.setCollectionKey(newValue);
  }
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
      title="Close Filter Panel"
      @click="closePanel"
    />
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
            title="Reset Year Filters"
            >(clear filter)</q-btn
          >
        </div>
      </q-card-section>
      <q-card-section class="q-pt-xs q-pb-lg q-pt-md q-pl-lg">
        <div>
          <svg
            :width="yearVisWidth"
            :height="yearVisHeight"
            @pointermove="mouseMoveInSvg"
            @pointerleave="mouseOutSvg"
            @click="clickInSvg"
            ref="svgContainer"
          >
            <g v-if="paperDataStore.papers.length > 0" class="right-label">
              <line :x1="barChartLabelX" :x2="barChartLabelX" y1="-2" y2="-5" />
              <text
                :x="barChartLabelX"
                y="-8"
                alignment-baseline="bottom"
                text-anchor="middle"
              >
                {{ paperDataStore.maxPapersInYear.count }}
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
                :class="
                  yearCount.year === selectedYear || selectedYear === null
                    ? 'selected'
                    : ''
                "
              ></rect>
            </g>
          </svg>
          <q-tooltip>
            <div class="text-h6">
              {{ selectedYearLabel }}: {{ totalSelectedPapers }}
            </div>
            <div
              class="text-subtitle1"
              v-for="[venue, count] in selectedPapersByVenue.entries()"
              :key="venue"
            >
              {{ venue }}: {{ count }}
            </div>
          </q-tooltip>
        </div>
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
            title="Reset Venue Filters"
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
            title="Reset Award Filters"
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
            title="Reset Resource Filters"
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
    <q-card flat>
      <q-card-section class="q-pb-none q-pt-none">
        <div class="text-h6">
          Collections
          <q-btn
            v-if="paperDataStore.collectionKey"
            padding="xs"
            size="sm"
            flat
            no-caps
            class="text-caption"
            @click="collectionKeyMirror = null"
            title="Remove Collection Filter"
            >(clear filter)</q-btn
          >
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none flex justify-between">
        <q-select
          class="full-width"
          dense
          clearable
          full-width
          rounded
          outlined
          v-model="collectionKeyMirror"
          :options="collectionKeyOptions"
        />
        <div class="q-mt-sm" v-if="paperDataStore.paperCollection">
          <div class="text-subtitle2">
            {{ paperDataStore.paperCollection.title }}
          </div>
          <div class="text-body2">
            {{ paperDataStore.paperCollection.description }}
          </div>
        </div>
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
  fill: $grey;
}

.bars .selected {
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
