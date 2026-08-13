import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { defineStore } from 'pinia';

export type PluginOrientation = 'horizontal' | 'vertical';

export const usePluginStore = defineStore('pluginStore', () => {
  const { currentRoute, push } = useRouter();

  function updateQueryState(params: {
    [parameter: string]: string | null;
  }): void {
    const query = { ...currentRoute.value.query };
    for (const parameter in params) {
      const value = params[parameter];
      if (query[parameter] === value) continue;
      if (value === null) {
        delete query[parameter];
      } else {
        query[parameter] = value;
      }
    }
    push({ query }).catch((e) => {
      console.log(e);
    });
  }

  const pluginUrl = ref<string | null>(
    (currentRoute.value.query.plugin as string) ?? null
  );

  const pluginOrientation = ref<PluginOrientation>(
    currentRoute.value.query.pluginOrientation === 'vertical'
      ? 'vertical'
      : 'horizontal'
  );

  // Session-scoped set of URLs the user has approved in this tab.
  // Not URL-synced — sharing a link must always re-prompt.
  const trustedUrls = ref<Set<string>>(new Set<string>());

  watch(
    currentRoute,
    (to, from) => {
      if (to.query.plugin !== from.query.plugin) {
        pluginUrl.value = (to.query.plugin as string) ?? null;
      }
      if (to.query.pluginOrientation !== from.query.pluginOrientation) {
        pluginOrientation.value =
          to.query.pluginOrientation === 'vertical' ? 'vertical' : 'horizontal';
      }
    },
    { deep: true }
  );

  function setPluginUrl(url: string | null): void {
    pluginUrl.value = url;
    updateQueryState({ plugin: url });
  }

  function closePlugin(): void {
    setPluginUrl(null);
  }

  function toggleOrientation(): void {
    const next: PluginOrientation =
      pluginOrientation.value === 'horizontal' ? 'vertical' : 'horizontal';
    pluginOrientation.value = next;
    // Horizontal is the default — omit from the URL when default.
    updateQueryState({
      pluginOrientation: next === 'horizontal' ? null : next,
    });
  }

  function trustUrl(url: string): void {
    trustedUrls.value.add(url);
  }

  function isTrusted(url: string): boolean {
    return trustedUrls.value.has(url);
  }

  return {
    pluginUrl,
    pluginOrientation,
    setPluginUrl,
    closePlugin,
    toggleOrientation,
    trustUrl,
    isTrusted,
  };
});
