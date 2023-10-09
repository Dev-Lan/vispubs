import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { parse, type ParseResult } from 'papaparse';

export interface AuthorState {
  websites: Map<string, string>;
  loading: boolean;
  // doubleCount: number;
  // increment: () => void;
}

export const useAuthorStore = defineStore('authorStore', () => {
  const websites = ref<Map<string, string>>(new Map());
  const loading = ref<boolean>(true);
  parse(window.location.origin + '/data/authors.csv', {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    download: true,
    // worker: true,
    comments: '#',
    // transformHeader,
    complete: (results: ParseResult<any>, _file: string) => {
      // console.log(results);
      //   allData.value = results.data;
      for (const { author, website } of results.data) {
        websites.value.set(author, website);
      }
      loading.value = false;
      // console.log('author loading complete');
    },
  });

  return { websites, loading };
});
