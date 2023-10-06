import { ref, computed } from 'vue';
import { defineStore } from 'pinia';

import { parse, type ParseResult } from 'papaparse';

export interface PaperInfo {
  title: string;
  authorNames: string;
  doi: string;
  year: number;
  abstract: string;
  conferenct: string;
}

export interface PaperDataStoreState {
  allData: PaperInfo[] | null;
}

export const usePaperDataStore = defineStore('paperDataStore', () => {
  const allData = ref<PaperInfo[] | null>(null);

  function transformHeader(header: string, _index: number): string {
    if (header === 'DOI') return 'doi';
    if (header === 'authorNames-Deduped') return 'authorNamesDeduped';
    return header.slice(0, 1).toLowerCase() + header.slice(1);
  }

  parse(window.location.origin + '/data/VIS.csv', {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    download: true,
    // worker: true,
    comments: '#',
    transformHeader,
    complete: (results: ParseResult<any>, _file: string) => {
      console.log(results);
      allData.value = results.data;
    },
  });

  return { allData };
});
