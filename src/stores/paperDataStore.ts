import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { debounce } from 'quasar';

import { parse, type ParseResult } from 'papaparse';

export interface PaperInfo {
  title: string;
  authorNamesDeduped: string;
  doi: string;
  year: number;
  abstract: string;
  conference: string;
  award: string;
  resources?: string;
  link?: string;
}

export interface PaperDataStoreState {
  allData: PaperInfo[] | null;
}

export interface PaperResourceLink {
  name: string;
  url: string;
  icon: 'paper' | 'video' | 'code' | 'project_website' | 'data' | 'other';
}

export const usePaperDataStore = defineStore('paperDataStore', () => {
  const { currentRoute, push, replace } = useRouter();

  function updateQueryState(
    parameter: string,
    value: string | null,
    options?: {
      replaceState?: boolean;
      forceUpdate?: boolean;
    }
  ): void {
    if (
      currentRoute.value.query[parameter] === value &&
      !options?.forceUpdate
    ) {
      // check if the parameter is already in the query
      return;
    }
    let query;

    if (value === null) {
      query = { ...currentRoute.value.query };
      delete query[parameter];
    } else {
      query = {
        ...currentRoute.value.query,
        [parameter]: value,
      };
    }
    if (options?.replaceState) {
      replace({ query });
    } else {
      push({
        query,
      }).catch((e) => {
        console.log(e);
      });
    }
  }

  watch(
    currentRoute,
    (to, from) => {
      // changes to paper
      const toPaper = to.query.paper;
      const fromPaper = from.query.paper;
      if (toPaper !== fromPaper && toPaper !== selectedPaper.value?.doi) {
        if (toPaper == null) {
          deselectPaper();
        } else {
          selectPaperByDoi(toPaper as string);
        }
      }

      // changes to matchCase
      if (to.query.matchCase !== from.query.matchCase) {
        matchCase.value = (to.query.matchCase as string) ?? null;
      }

      // changes to useRegex
      if (to.query.useRegex !== from.query.useRegex) {
        useRegex.value = (to.query.useRegex as string) ?? null;
      }

      // changes to searchText
      if (to.query.searchText !== from.query.searchText) {
        searchText.value = (to.query.searchText as string) ?? '';
      }
    },
    { deep: true }
  );

  const allData = ref<PaperInfo[] | null>(null);

  const selectedPaper = ref<PaperInfo | null>(null);
  const selectedPaperIndex = ref<number | null>(null);
  const focusedPaperIndex = ref<number | null>(null);

  const selectedPaperResourceLinks = ref<PaperResourceLink[]>([]);

  function selectFocusedPaper(): void {
    if (focusedPaperIndex.value === null) return;
    selectPaper(focusedPaperIndex.value);
  }

  function selectPaperByDoi(doi: string): void {
    if (papers.value === null) return;
    const selectedIndex = papers.value.findIndex(
      (paperInfo: PaperInfo) => paperInfo.doi === doi
    );
    if (selectedIndex >= 0) {
      selectPaper(selectedIndex);
    }
  }

  function selectPaper(index: number): void {
    if (papers.value === null) return;
    selectedPaperIndex.value = index;
    selectedPaper.value = papers.value[index];

    updateQueryState('paper', selectedPaper.value?.doi);

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
        // console.log('parsed paper resources');
        // console.log(results);
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
    updateQueryState('paper', null);
  }

  function clearFocusedPaper(): void {
    focusedPaperIndex.value = null;
  }

  function focusPaper(index: number): void {
    focusedPaperIndex.value = index;
  }

  function focusPreviousPaper(): void {
    if (focusedPaperIndex.value === null) {
      return;
    }
    if (focusedPaperIndex.value === 0) return;
    focusedPaperIndex.value = focusedPaperIndex.value - 1;
  }

  function focusNextPaper(): void {
    if (focusedPaperIndex.value === null) {
      focusedPaperIndex.value = 0;
      return;
    }
    if (focusedPaperIndex.value === papers.value.length - 1) return;
    focusedPaperIndex.value = focusedPaperIndex.value + 1;
  }

  const progressDisplay = computed<string>(() => {
    if (selectedPaperIndex.value === null) return '';
    if (papers.value === null) return '';
    return `${selectedPaperIndex.value + 1} of ${papers.value.length}`;
  });

  function getAward(key: string): string {
    if (key === 'HM') return 'Honorable Mention';
    if (key === 'BP') return 'Best Paper';
    if (key === 'TT') return 'Test of Time';
    if (key === 'BA') return 'Best Application';
    if (key === 'BCS') return 'Best Case Study';
    return 'Unknown Award';
  }

  function getResourceColor(icon: string): string {
    switch (icon) {
      case 'paper':
      case 'P':
        return 'indigo';
      case 'video':
      case 'V':
        return 'red';
      case 'code':
      case 'C':
        return 'green-10';
      case 'data':
      case 'D':
        return 'purple';
      case 'project_website':
      case 'PW':
        return 'teal';
      default:
        return 'blue-grey';
    }
  }

  function getResourceTextColor(icon: string): string {
    // if (icon === 'other' || icon === 'O') return 'black';
    return 'white';
  }

  function getResourceIcon(icon: string): string {
    switch (icon) {
      case 'paper':
      case 'P':
        return 'article';
      case 'video':
      case 'V':
        return 'ondemand_video';
      case 'code':
      case 'C':
        return 'code';
      case 'data':
      case 'D':
        return 'storage';
      case 'project_website':
      case 'PW':
        return 'language';
      default:
        return 'open_in_new';
    }
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
      const currentPaperDOI = currentRoute.value.query.paper;
      if (currentPaperDOI) {
        selectPaperByDoi(currentPaperDOI as string);
      }
    },
  });

  function transformHeader(header: string, _index: number): string {
    if (header === 'DOI') return 'doi';
    if (header === 'AuthorNames-Deduped') return 'authorNamesDeduped';
    return header.slice(0, 1).toLowerCase() + header.slice(1);
  }

  const searchText = ref<string | null>(
    (currentRoute.value.query.searchText as string) ?? ''
  );
  watch(searchText, () => {
    debouncedPushSearchTextState();
  });

  const debouncedPushSearchTextState = debounce(pushSearchTextState, 1000);

  function pushSearchTextState(): void {
    if (searchText.value === '') {
      updateQueryState('searchText', null, { forceUpdate: true });
      return;
    }
    updateQueryState('searchText', searchText.value, { forceUpdate: true });
  }

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

  const matchCase = ref<string | null>(
    (currentRoute.value.query.matchCase as string) ?? null
  );
  watch(matchCase, () => {
    if (matchCase.value === null) {
      updateQueryState('matchCase', null);
      return;
    }
    updateQueryState('matchCase', matchCase.value);
  });

  const useRegex = ref<string | null>(
    (currentRoute.value.query.useRegex as string) ?? null
  );
  watch(useRegex, () => {
    if (useRegex.value === null) {
      updateQueryState('useRegex', null);
      return;
    }
    updateQueryState('useRegex', useRegex.value);
  });

  function getKeyList(string?: string): string[] {
    if (!string) {
      return [];
    }
    return string.split(';');
  }

  return {
    allData,
    selectedPaper,
    selectedPaperResourceLinks,
    previousPaper,
    nextPaper,
    clearFocusedPaper,
    focusPaper,
    focusPreviousPaper,
    focusNextPaper,
    selectedPaperIndex,
    focusedPaperIndex,
    progressDisplay,
    selectPaper,
    selectFocusedPaper,
    deselectPaper,
    getKeyList,
    getAward,
    getResourceColor,
    getResourceTextColor,
    getResourceIcon,
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
