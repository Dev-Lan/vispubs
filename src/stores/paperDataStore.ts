import { ref, computed, watch } from 'vue';
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
  link?: string;
}

export interface PaperDataStoreState {
  allData: PaperInfo[] | null;
}

export interface PaperResourceLink {
  name: string;
  url: string;
  icon: 'paper' | 'video' | 'code' | 'project' | 'data' | 'other';
}

export const usePaperDataStore = defineStore('paperDataStore', () => {
  const params = useUrlSearchParams('history');

  const allData = ref<PaperInfo[] | null>(null);

  const selectedPaper = ref<PaperInfo | null>(null);
  const selectedPaperIndex = ref<number | null>(null);

  const selectedPaperResourceLinks = ref<PaperResourceLink[]>([]);

  function selectPaper(index: number): void {
    if (papers.value === null) return;
    selectedPaperIndex.value = index;
    selectedPaper.value = papers.value[index];
    params.paper = selectedPaper.value?.doi;
    selectedPaperResourceLinks.value = [];
    if (!selectedPaper.value?.doi) return;
    const doi = selectedPaper.value.doi;
    const csvPath = window.location.origin + '/data/paperLinks/' + doi;
    parse(csvPath, {
      header: true,
      dynamicTyping: false,
      skipEmptyLines: true,
      download: true,
      // worker: true,
      comments: '#',
      complete: (results: ParseResult<any>, _file: string) => {
        console.log('parsed paper resources');
        console.log(results);
        selectedPaperResourceLinks.value = results.data;
      },
    });
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
        const selectedIndex = papers.value.findIndex(
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

  const searchText = ref<string>(params.search ?? '');

  watch(searchText, () => {
    if (searchText.value === '') {
      params.search = null;
      return;
    }
    params.search = searchText.value;
  });

  const allPapers = ref();

  const validRegex = computed<boolean>(() => {
    if (useRegex.value === null) {
      regexErrorString.value = '';
      return true;
    }
    try {
      new RegExp(searchText.value);
    } catch (e: Error) {
      console.log('setting regex error string');
      console.log({ e });
      regexErrorString.value = e.message;
      return false;
    }
    regexErrorString.value = '';
    return true;
  });

  const regexErrorString = ref<string>('');

  const papers = computed<PaperInfo[]>(() => {
    if (searchText.value === '') return allPapers.value;
    const ignoreCase = matchCase.value === null;
    let regex: RegExp | null = null;
    if (useRegex.value !== null) {
      try {
        regex = ignoreCase
          ? new RegExp(searchText.value, 'mi')
          : new RegExp(searchText.value, 'm');
      } catch (e) {
        return [];
      }
    }
    let query = searchText.value;
    if (ignoreCase) {
      query = query.toLowerCase();
    }
    return allPapers.value.filter((paper: PaperInfo) => {
      return paperMatchesQuery(regex ?? query, paper);
    });
  });

  const papersWithLinks = computed<PaperInfo[]>(() => {
    if (papers.value === null) return [];
    if (papers.value.length === 0) return [];
    const currentUrl = window.location.href;
    return papers.value.map((paper: PaperInfo) => {
      const url = new URL(currentUrl);
      url.searchParams.set('paper', paper.doi);
      return {
        ...paper,
        link: url.toString(),
      };
    });
  });

  function paperMatchesQuery(
    query: string | RegExp,
    paper: PaperInfo
  ): boolean {
    const textArray: string[] = [];
    const authors = getAuthors(paper);
    for (const author of authors) {
      textArray.push(author.displayName ?? '');
    }
    textArray.push(paper.title ?? '');
    textArray.push(paper.abstract ?? '');
    // combine all text into one string so regex can match across fields
    // use ¶ as a separator because it is an unlikely character in the text
    return textMatchesQuery(query, textArray.join('¶'));
  }

  function textMatchesQuery(query: string | RegExp, text: string): boolean {
    if (typeof query !== 'string') {
      // evaluate regex
      return query.test(text);
    }
    if (matchCase.value === null) {
      text = text.toLowerCase();
    }
    return text.includes(query);
  }

  const matchCase = ref<string | null>(params.matchCase ?? null);
  watch(matchCase, () => {
    params.matchCase = matchCase.value;
  });

  const useRegex = ref<string | null>(params.useRegex ?? null);
  watch(useRegex, () => {
    params.useRegex = useRegex.value;
  });

  return {
    allData,
    selectedPaper,
    selectedPaperResourceLinks,
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
    papersWithLinks,
    searchText,
    matchCase,
    useRegex,
    validRegex,
    regexErrorString,
  };
});
