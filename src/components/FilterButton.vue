<script setup lang="ts">
const props = defineProps<{
  text: string;
  count: number;
  maxCount: number;
  selected: boolean;
  width?: number;
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
      <span
        :class="props.selected ? 'text-weight-bolder' : 'text-weight-regular'"
        >{{ props.text }}</span
      >
      <span class="q-ml-xs text-caption"> ({{ props.count }})</span>
    </q-btn>
    <div class="underline">
      <div
        class="underline-data"
        :style="`width: ${(100 * props.count) / props.maxCount}%`"
      ></div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.underline {
  background: rgba(125, 125, 125, 0.2);
  height: 2px;
}

.underline-data {
  background-color: $primary;
  height: 2px;
}
</style>
