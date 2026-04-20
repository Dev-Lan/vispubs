<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { debounce, useQuasar } from 'quasar';

import { usePluginStore } from 'src/stores/pluginStore';
import { usePaperDataStore, type PaperInfo } from 'src/stores/paperDataStore';
import { useGlobalStore } from 'src/stores/globalStore';

import type {
  PluginFilterState,
  PluginPaper,
  PluginStatePayload,
  PluginToHostMessage,
} from 'src/types/plugin';

const $q = useQuasar();
const pluginStore = usePluginStore();
const paperDataStore = usePaperDataStore();
const globalStore = useGlobalStore();

const iframeRef = ref<HTMLIFrameElement | null>(null);
const pluginReady = ref<boolean>(false);
const dialogOpen = ref<boolean>(false);

const originLabel = computed<string>(() => {
  if (!pluginStore.pluginUrl) return '';
  try {
    return new URL(pluginStore.pluginUrl, window.location.origin).origin;
  } catch {
    return pluginStore.pluginUrl;
  }
});

const iframeSrc = computed<string | null>(() => {
  const url = pluginStore.pluginUrl;
  if (!url) return null;
  if (!pluginStore.isTrusted(url)) return null;
  return url;
});

function toPluginPaper(p: PaperInfo): PluginPaper {
  return {
    doi: p.doi,
    title: p.title,
    year: p.year,
    conference: p.conference,
    award: p.award,
    authorNamesDeduped: p.authorNamesDeduped,
    abstract: p.abstract,
    resources: p.resources,
    accessible: p.accessible,
    early: p.early,
  };
}

function buildFilterState(): PluginFilterState {
  return {
    searchText: paperDataStore.searchText ?? '',
    matchCase: paperDataStore.matchCase !== null,
    useRegex: paperDataStore.useRegex !== null,
    yearFilter: paperDataStore.yearFilterSet
      ? {
          min: paperDataStore.yearFilter.min,
          max: paperDataStore.yearFilter.max,
        }
      : null,
    venueFilter: Array.from(paperDataStore.venueFilter).sort(),
    awardFilter: Array.from(paperDataStore.awardFilter).sort(),
    resourceFilter: Array.from(paperDataStore.resourceFilter).sort(),
    collection: paperDataStore.collectionKey ?? null,
  };
}

function buildState(): PluginStatePayload {
  const focusIdx = paperDataStore.focusedPaperIndex;
  const focusedDoi =
    focusIdx != null && paperDataStore.papers[focusIdx]
      ? paperDataStore.papers[focusIdx].doi
      : null;
  return {
    type: 'vispubs:state',
    papers: paperDataStore.papers.map(toPluginPaper),
    filters: buildFilterState(),
    selectedDoi: paperDataStore.selectedPaper?.doi ?? null,
    focusedDoi,
    darkMode: globalStore.darkMode,
  };
}

function postState(): void {
  if (!pluginReady.value) return;
  const win = iframeRef.value?.contentWindow;
  if (!win) return;
  win.postMessage(buildState(), '*');
}

const debouncedPostState = debounce(postState, 150);

function onMessage(event: MessageEvent): void {
  const iframe = iframeRef.value;
  if (!iframe || event.source !== iframe.contentWindow) return;

  const data = event.data as { type?: unknown } | null;
  if (!data || typeof data.type !== 'string') return;
  if (!data.type.startsWith('vispubs:')) return;

  const msg = data as PluginToHostMessage;
  switch (msg.type) {
    case 'vispubs:ready':
      pluginReady.value = true;
      postState();
      return;
    case 'vispubs:selectPaper':
      if (typeof msg.doi === 'string') {
        const index = paperDataStore.papers.findIndex(
          (p) => p.doi === msg.doi
        );
        if (index >= 0) paperDataStore.selectPaper(index);
      }
      return;
    case 'vispubs:focusPaper':
      if (msg.doi == null) {
        paperDataStore.clearFocusedPaper();
        return;
      }
      if (typeof msg.doi === 'string') {
        const index = paperDataStore.papers.findIndex(
          (p) => p.doi === msg.doi
        );
        if (index >= 0) paperDataStore.focusedPaperIndex = index;
      }
      return;
  }
}

watch(
  () => [
    paperDataStore.papers,
    paperDataStore.selectedPaper?.doi,
    paperDataStore.focusedPaperIndex,
    globalStore.darkMode,
  ],
  () => debouncedPostState(),
  { deep: true }
);

function maybePromptAndLoad(): void {
  const url = pluginStore.pluginUrl;
  if (!url) return;
  if (pluginStore.isTrusted(url)) return;
  if (dialogOpen.value) return;

  dialogOpen.value = true;
  $q.dialog({
    title: 'Load third-party plugin?',
    message:
      `<p>This page wants to load a plugin from <b>${escapeHtml(
        originLabel.value
      )}</b>.</p>` +
      `<p>Plugins run in a sandboxed iframe and can display visualizations using the public paper data. They cannot read your cookies, local storage, or anything else on vispubs.com.</p>` +
      '<p>Only load plugins from sources you trust.</p>',
    html: true,
    persistent: true,
    ok: { label: 'Load plugin', color: 'primary' },
    cancel: { label: 'Cancel', flat: true },
  })
    .onOk(() => {
      pluginStore.trustUrl(url);
    })
    .onCancel(() => {
      pluginStore.closePlugin();
    })
    .onDismiss(() => {
      dialogOpen.value = false;
    });
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

watch(
  () => pluginStore.pluginUrl,
  () => {
    pluginReady.value = false;
    maybePromptAndLoad();
  }
);

onMounted(() => {
  window.addEventListener('message', onMessage);
  maybePromptAndLoad();
});

onBeforeUnmount(() => {
  window.removeEventListener('message', onMessage);
});

function close(): void {
  pluginStore.closePlugin();
}
</script>

<template>
  <div class="plugin-host column">
    <div class="plugin-host__header row items-center q-px-sm q-py-xs">
      <q-icon name="extension" size="sm" class="q-mr-sm" />
      <div
        class="plugin-host__title ellipsis"
        :title="pluginStore.pluginUrl ?? ''"
      >
        Plugin · {{ originLabel }}
      </div>
      <q-space />
      <q-btn
        dense
        flat
        round
        :icon="
          pluginStore.pluginOrientation === 'horizontal'
            ? 'swap_horiz'
            : 'swap_vert'
        "
        :title="`Switch to ${
          pluginStore.pluginOrientation === 'horizontal'
            ? 'vertical'
            : 'horizontal'
        } layout`"
        @click="pluginStore.toggleOrientation()"
      />
      <q-btn
        dense
        flat
        round
        icon="close"
        title="Close plugin"
        @click="close"
      />
    </div>
    <div class="plugin-host__body col">
      <iframe
        v-if="iframeSrc"
        ref="iframeRef"
        :src="iframeSrc"
        sandbox="allow-scripts"
        class="plugin-host__iframe"
      />
      <div v-else class="plugin-host__placeholder text-center q-pa-md">
        Waiting for plugin approval…
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.plugin-host {
  width: 100%;
  height: 100%;
  min-height: 0;
  min-width: 0;
  border: 1px solid rgba(128, 128, 128, 0.3);
}
.plugin-host__header {
  border-bottom: 1px solid rgba(128, 128, 128, 0.3);
  background: rgba(128, 128, 128, 0.08);
  flex: 0 0 auto;
}
.plugin-host__title {
  font-size: 0.9rem;
  max-width: 60%;
}
.plugin-host__body {
  position: relative;
  min-height: 0;
  min-width: 0;
}
.plugin-host__iframe {
  width: 100%;
  height: 100%;
  border: 0;
  display: block;
}
.plugin-host__placeholder {
  color: rgba(128, 128, 128, 0.8);
}
</style>
