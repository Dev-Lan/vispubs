<script setup lang="ts">
import SimpleBar from './SimpleBar.vue';
import { usePaperDataStore } from 'src/stores/paperDataStore';
const paperDataStore = usePaperDataStore();

const props = defineProps<{
  text: string;
  count: number;
  maxCount: number;
  selected: boolean;
  width?: number;
  icon?: string;
}>();

const emit = defineEmits(['click']);

function onClick(event: Event) {
  emit('click');
  event?.stopPropagation();
}
</script>

<template>
  <div class="q-mb-xs" :style="`width: ${props.width ?? 45}%`">
    <q-btn
      dense
      flat
      align="left"
      class="full-width"
      no-caps
      :title="`${props.selected ? 'Remove' : 'Add'} Filter: ${props.text} `"
      @click="onClick($event)"
    >
      <q-avatar
        v-if="props.icon"
        :color="paperDataStore.getResourceColor(props.icon)"
        :text-color="paperDataStore.getResourceTextColor(props.icon)"
        :icon="paperDataStore.getResourceIcon(props.icon)"
        size="xs"
        class="q-mr-xs font-size-override"
      />
      <span
        :class="props.selected ? 'text-weight-bolder' : 'text-weight-regular'"
        >{{ props.text }}</span
      >
      <span class="q-ml-xs text-caption"> ({{ props.count }})</span>
    </q-btn>
    <SimpleBar
      :show-grey="false"
      :count="props.count"
      :maxCount="props.maxCount"
    ></SimpleBar>
  </div>
</template>

<style lang="scss">
// the style must not be scoped (in order to grab the q-icon class)
.font-size-override .q-icon {
  // Quasar probably doesn't expect avatars in buttons and they have
  // specific font sizes for icons in buttons we need to override
  font-size: inherit !important;
}
</style>
