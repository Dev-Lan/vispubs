<script setup lang="ts">
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
    <div class="vispubs-underline">
      <div
        class="vispubs-underline-data"
        :style="`width: ${
          props.maxCount === 0 ? 0 : (100 * props.count) / props.maxCount
        }%`"
      ></div>
    </div>
  </div>
</template>

<style lang="scss">
.vispubs-underline {
  background: rgba(125, 125, 125, 0.2);
  height: 2px;
}

.vispubs-underline-data {
  background-color: $primary;
  height: 2px;
}
// this is also requires this style to not be scoped (in order to grab the q-icon class)
// hence the vispubs- prefix.
.font-size-override .q-icon {
  // Quasar probably doesn't expect avatars in buttons and they have
  // specific font sizes for icons in buttons we need to override
  font-size: inherit !important;
}
</style>
