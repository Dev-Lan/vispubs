import { ref, computed } from 'vue';
import { defineStore } from 'pinia';

import { parse, type ParseResult } from 'papaparse';

export interface PaperInfo {
  title: string;
  authorNames: string;
  authorNamesDeduped: string;
  doi: string;
  year: number;
  abstract: string;
  conference: string;
  award: string;
}

export interface PaperDataStoreState {
  allData: PaperInfo[] | null;
}

export const usePaperDataStore = defineStore('paperDataStore', () => {
  const allData = ref<PaperInfo[] | null>(null);

  const selectedPaper = ref<PaperInfo | null>(null);
  const selectedPaperIndex = ref<number | null>(null);

  function selectPaper(index: number): void {
    if (allData.value === null) return;
    selectedPaperIndex.value = index;
    selectedPaper.value = allData.value[index];
  }

  function previousPaper(): void {
    if (allData.value === null) return;
    if (selectedPaperIndex.value === null) {
      selectPaper(0);
      return;
    }
    selectPaper(Math.max(selectedPaperIndex.value - 1, 0));
  }

  function nextPaper(): void {
    if (allData.value === null) return;
    if (selectedPaperIndex.value === null) {
      selectPaper(0);
      return;
    }
    selectPaper(
      Math.min(selectedPaperIndex.value + 1, allData.value.length - 1)
    );
  }

  function deselectPaper(): void {
    selectedPaper.value = null;
    selectedPaperIndex.value = null;
  }

  const progressDisplay = computed<string>(() => {
    if (selectedPaperIndex.value === null) return '';
    if (allData.value === null) return '';
    return `${selectedPaperIndex.value + 1} of ${allData.value.length}`;
  });

  function getAward(paperInfo: PaperInfo): string {
    const key = paperInfo.award;
    if (key === 'HM') return 'Honorable Mention';
    if (key === 'TT') return 'Test of Time';
    if (key === 'BP') return 'Best Paper';
    return 'Unknown Award';
  }

  function getConference(paperInfo: PaperInfo): string {
    const key = paperInfo.conference;
    if (key === 'Vis') return 'VIS';
    return key;
  }

  function getAuthors(paperInfo: PaperInfo): string[] {
    const authors = paperInfo.authorNamesDeduped;
    if (authors == null) {
      return [];
    }
    const authorList = authors.split(';').map((name: string) => {
      const nameChunks = name.split(' ').filter((chunk: string) => {
        return isNaN(parseInt(chunk));
      });
      return nameChunks.join(' ');
    });
    return authorList;
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

  function transformHeader(header: string, _index: number): string {
    if (header === 'DOI') return 'doi';
    if (header === 'AuthorNames-Deduped') return 'authorNamesDeduped';
    return header.slice(0, 1).toLowerCase() + header.slice(1);
  }

  return {
    allData,
    selectedPaper,
    previousPaper,
    nextPaper,
    selectedPaperIndex,
    progressDisplay,
    selectPaper,
    deselectPaper,
    getAward,
    getConference,
    getAuthors,
  };
});
