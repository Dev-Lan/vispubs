import { ref, computed } from 'vue';
import { defineStore } from 'pinia';

import { parse, type ParseResult } from 'papaparse';

import { useUrlSearchParams } from '@vueuse/core';

export interface PaperInfo {
  title: string;
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
  const params = useUrlSearchParams('hash');

  const allData = ref<PaperInfo[] | null>(null);

  const selectedPaper = ref<PaperInfo | null>(null);
  const selectedPaperIndex = ref<number | null>(null);

  function selectPaper(index: number): void {
    if (papers.value === null) return;
    selectedPaperIndex.value = index;
    selectedPaper.value = papers.value[index];
    params.paper = selectedPaper.value?.doi;
  }

  function previousPaper(): void {
    if (papers.value === null) return;
    if (selectedPaperIndex.value === null) {
      selectPaper(0);
      return;
    }
    selectPaper(Math.max(selectedPaperIndex.value - 1, 0));
  }

  function nextPaper(): void {
    if (papers.value === null) return;
    if (selectedPaperIndex.value === null) {
      selectPaper(0);
      return;
    }
    selectPaper(
      Math.min(selectedPaperIndex.value + 1, papers.value.length - 1)
    );
  }

  function deselectPaper(): void {
    selectedPaper.value = null;
    selectedPaperIndex.value = null;
    params.paper = null;
  }

  const progressDisplay = computed<string>(() => {
    if (selectedPaperIndex.value === null) return '';
    if (papers.value === null) return '';
    return `${selectedPaperIndex.value + 1} of ${papers.value.length}`;
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

  interface AuthorName {
    displayName: string; // e.g. 'Devin Lange'
    dedupedName: string; //  e.g. 'Devin Lange 0007'
  }

  function getAuthors(paperInfo: PaperInfo): AuthorName[] {
    const authors = paperInfo.authorNamesDeduped;
    if (authors == null) {
      return [];
    }
    const authorList = authors.split(';').map((name: string) => {
      const nameChunks = name.split(' ').filter((chunk: string) => {
        return isNaN(parseInt(chunk));
      });
      const displayName = nameChunks.join(' ');
      return { displayName, dedupedName: name };
    });
    return authorList;
  }

  parse(window.location.origin + '/data/papers.csv', {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    download: true,
    // worker: true,
    comments: '#',
    transformHeader,
    complete: (results: ParseResult<any>, _file: string) => {
      // console.log(results);
      allData.value = results.data;
      allPapers.value = JSON.parse(JSON.stringify(allData.value));
      if (params.paper) {
        const selectedIndex = allData.value.findIndex(
          (paperInfo: PaperInfo) => paperInfo.doi === params.paper
        );
        if (selectedIndex >= 0) {
          selectPaper(selectedIndex);
        }
      }
    },
  });

  function transformHeader(header: string, _index: number): string {
    if (header === 'DOI') return 'doi';
    if (header === 'AuthorNames-Deduped') return 'authorNamesDeduped';
    return header.slice(0, 1).toLowerCase() + header.slice(1);
  }

  const searchText = ref<string>('');
  const allPapers = ref();
  const papers = computed<PaperInfo[]>(() => {
    if (searchText.value === '') return allPapers.value;
    return allPapers.value.filter((paper: PaperInfo) => {
      return paperMatchesQuery(searchText.value, paper);
    });
  });

  function paperMatchesQuery(
    query: string,
    paper: PaperInfo,
    matchCase = false,
    useRegex = false
  ): boolean {
    const authors = getAuthors(paper);
    for (const author of authors) {
      if (
        textMatchesQuery(query, author.displayName ?? '', matchCase, useRegex)
      ) {
        return true;
      }
    }
    return (
      textMatchesQuery(query, paper.title ?? '', matchCase, useRegex) ||
      textMatchesQuery(query, paper.abstract ?? '', matchCase, useRegex)
    );
  }

  function textMatchesQuery(
    query: string,
    text: string,
    matchCase = false,
    useRegex = false
  ): boolean {
    if (!matchCase) {
      query = query.toLowerCase();
      text = text.toLowerCase();
    }
    if (useRegex) {
      return text.match(query) !== null;
    }
    return text.includes(query);
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
    papers,
    searchText,
  };
});
