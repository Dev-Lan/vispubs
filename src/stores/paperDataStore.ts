/* eslint-disable @typescript-eslint/ban-ts-comment */
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
    params: { [parameter: string]: string | null },
    options?: {
      replaceState?: boolean;
      forceUpdate?: boolean;
    }
  ): void {
    const query = { ...currentRoute.value.query };

    for (const parameter in params) {
      const value = params[parameter];

      if (query[parameter] === value && !options?.forceUpdate) {
        // check if the parameter is already in the query
        continue;
      }

      if (value === null) {
        delete query[parameter];
      } else {
        query[parameter] = value;
      }
    }

    if (options?.replaceState) {
      replace({ query });
    } else {
      push({ query }).catch((e) => {
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

      // changes to year filter
      if (to.query.minYear !== from.query.minYear) {
        if (to.query.minYear != null) {
          yearFilter.value.min = parseInt(to.query.minYear as string);
        } else {
          yearFilter.value.min = yearExtent.value?.[0] ?? -Infinity;
        }
      }
      if (to.query.maxYear !== from.query.maxYear) {
        if (to.query.maxYear != null) {
          yearFilter.value.max = parseInt(to.query.maxYear as string);
        } else {
          yearFilter.value.max = yearExtent.value?.[1] ?? Infinity;
        }
      }

      // changes to filterPanelOpen
      if (to.query.filterPanelOpen !== from.query.filterPanelOpen) {
        filterPanelOpen.value = to.query.filterPanelOpen === 'true';
      }

      // changes to venueFilter
      if (to.query.venueFilter !== from.query.venueFilter) {
        venueFilter.value = new Set<string>(
          (to.query.venueFilter as string)?.split(',') ?? []
        );
      }

      // changes to awardFilter
      if (to.query.awardFilter !== from.query.awardFilter) {
        awardFilter.value = new Set<string>(
          (to.query.awardFilter as string)?.split(',') ?? []
        );
      }

      // changes to resourceFilter
      if (to.query.resourceFilter !== from.query.resourceFilter) {
        resourceFilter.value = new Set<string>(
          (to.query.resourceFilter as string)?.split(',') ?? []
        );
      }
    },
    { deep: true }
  );

  const allData = ref<PaperInfo[] | null>(null);

  const selectedPaper = ref<PaperInfo | null>(null);
  const selectedPaperIndex = ref<number | null>(null);
  const focusedPaperIndex = ref<number | null>(null);
  const searchFocused = ref<boolean>(false);

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

    updateQueryState({ paper: selectedPaper.value?.doi });

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
    updateQueryState({ paper: null });
  }

  function clearFocusedPaper(): void {
    focusedPaperIndex.value = null;
  }

  function focusPaper(index: number): void {
    if (!searchFocused.value) return;
    focusedPaperIndex.value = index;
  }

  function focusPreviousPaper(): void {
    if (!searchFocused.value) return;
    if (focusedPaperIndex.value === null) {
      return;
    }
    if (focusedPaperIndex.value === 0) return;
    focusedPaperIndex.value = focusedPaperIndex.value - 1;
  }

  function focusNextPaper(): void {
    if (!searchFocused.value) return;
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

  function getResourceName(icon: string): string {
    switch (icon) {
      case 'paper':
      case 'P':
        return 'Paper';
      case 'video':
      case 'V':
        return 'Video';
      case 'code':
      case 'C':
        return 'Code';
      case 'data':
      case 'D':
        return 'Data';
      case 'project_website':
      case 'PW':
        return 'Website';
      default:
        return 'Other';
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
      updateQueryState({ searchText: null }, { forceUpdate: true });
      return;
    }
    updateQueryState({ searchText: searchText.value }, { forceUpdate: true });
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
    let filteredPapers = allPapers.value;
    if (filteredPapers == null) return [];
    if (searchText.value !== '') {
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
      filteredPapers = filteredPapers.filter((paper: PaperInfo) => {
        return paperMatchesQuery(regex ?? query, paper);
      });
    }
    if (yearFilterSet.value) {
      filteredPapers = filteredPapers.filter((paper: PaperInfo) => {
        return (
          paper.year >= (yearFilter.value?.min ?? -Infinity) &&
          paper.year <= (yearFilter.value?.max ?? Infinity)
        );
      });
    }
    if (venueFilter.value.size > 0) {
      filteredPapers = filteredPapers.filter((paper: PaperInfo) => {
        return venueFilter.value.has(getConference(paper));
      });
    }

    if (awardFilter.value.size > 0) {
      filteredPapers = filteredPapers.filter((paper: PaperInfo) => {
        for (const awardKey of getKeyList(paper.award)) {
          if (awardFilter.value.has(getAward(awardKey))) {
            return true;
          }
        }
        return false;
      });
    }

    if (resourceFilter.value.size > 0) {
      filteredPapers = filteredPapers.filter((paper: PaperInfo) => {
        for (const resourceKey of getKeyList(paper.resources)) {
          if (resourceFilter.value.has(getResourceName(resourceKey))) {
            return true;
          }
        }
        return false;
      });
    }
    return filteredPapers;
  });

  const yearFilterSet = computed<boolean>(() => {
    if (yearFilter.value == null || yearExtent.value == null) return false;
    if (
      yearFilter.value.min === -Infinity &&
      yearFilter.value.max === Infinity
    ) {
      return false;
    }
    if (
      yearFilter.value.min === yearExtent.value[0] &&
      yearFilter.value.max === yearExtent.value[1]
    ) {
      return false;
    }

    return true;
  });

  function clearYearFilter(): void {
    yearFilter.value = { min: -Infinity, max: Infinity };
  }

  interface PaperYearCount {
    year: number;
    count: number;
  }

  const paperYearCounts = computed<PaperYearCount[]>(() => {
    const yearCountMap = new Map<number, number>();
    if (papers.value == null) return [];
    for (const paper of papers.value) {
      const year = paper.year;
      if (!yearCountMap.has(year)) {
        yearCountMap.set(year, 0);
      }
      yearCountMap.set(year, yearCountMap.get(year)! + 1);
    }
    const yearCounts: PaperYearCount[] = [];
    for (const [year, count] of yearCountMap.entries()) {
      yearCounts.push({ year, count });
    }
    return yearCounts;
  });

  const yearExtent = computed<[number, number] | null>(() => {
    // use all papers, since x-axis should show all possible years
    if (allPapers.value == null) return null;
    const years = allPapers.value.map((paper: PaperInfo) => paper.year);
    return [Math.min(...years), Math.max(...years)];
  });

  let minYear: number | null = null;
  if (currentRoute.value.query.minYear) {
    minYear = parseInt(currentRoute.value.query.minYear as string);
  }

  let maxYear: number | null = null;
  if (currentRoute.value.query.maxYear) {
    maxYear = parseInt(currentRoute.value.query.maxYear as string);
  }

  const yearFilter = ref<{ min: number; max: number }>({
    min: minYear ?? -Infinity,
    max: maxYear ?? Infinity,
  });
  watch(
    yearExtent,
    () => {
      if (yearExtent.value === null) return;
      if (yearFilter.value.min === -Infinity) {
        yearFilter.value.min = yearExtent.value[0];
      }
      if (yearFilter.value.max === Infinity) {
        yearFilter.value.max = yearExtent.value[1];
      }
    },
    { deep: true }
  );

  watch(
    yearFilter,
    () => {
      debouncedPushYearFilterState();
    },
    { deep: true }
  );

  const debouncedPushYearFilterState = debounce(pushYearFilterState, 1000);

  function pushYearFilterState(): void {
    if (yearFilterSet.value) {
      console.log('setting yearFilterState');
      console.log(yearFilter.value);
      updateQueryState({
        minYear: yearFilter.value.min.toString(),
        maxYear: yearFilter.value.max.toString(),
      });
    } else {
      updateQueryState({ minYear: null, maxYear: null });
    }
  }

  // @ts-ignore
  const maxPapersInYear = computed<PaperYearCount>(() => {
    if (papers.value == null) return 0;
    // use filtered papers since the y-axis should be scaled to filtered data
    const maxCount = Math.max(
      ...paperYearCounts.value.map(
        (yearCount: PaperYearCount) => yearCount.count
      )
    );
    return paperYearCounts.value.find(
      (yearCount: PaperYearCount) => yearCount.count === maxCount
    );
  });

  const venues = computed<string[]>(() => {
    if (allPapers.value == null) return [];
    const venuesSet = new Set<string>();
    for (const paper of allPapers.value) {
      venuesSet.add(getConference(paper));
    }
    return Array.from(venuesSet);
  });

  interface VenueCount {
    venue: string;
    count: number;
  }
  const venueCounts = computed<VenueCount[]>(() => {
    const venueCountMap = new Map<string, number>();
    for (const venue of venues.value) {
      venueCountMap.set(venue, 0);
    }

    for (const paper of papers.value ?? []) {
      const venue = getConference(paper);
      venueCountMap.set(venue, venueCountMap.get(venue)! + 1);
    }

    const venueCounts: VenueCount[] = [];
    for (const [venue, count] of venueCountMap.entries()) {
      venueCounts.push({ venue, count });
    }

    venueCounts.sort((a: VenueCount, b: VenueCount) => {
      if (a.venue < b.venue) return -1;
      if (a.venue > b.venue) return 1;
      return 0;
    });
    return venueCounts;
  });

  const maxVenueCount = computed<number>(() => {
    if (venueCounts.value.length === 0) return 0;
    return Math.max(
      ...venueCounts.value.map((venueCount: VenueCount) => venueCount.count)
    );
  });

  const venueFilter = ref<Set<string>>(
    new Set<string>(
      (currentRoute.value.query.venueFilter as string)?.split(',') ?? []
    )
  );

  function toggleVenueFilter(venue: string): void {
    if (venueFilter.value.has(venue)) {
      venueFilter.value.delete(venue);
    } else {
      venueFilter.value.add(venue);
    }
    const venueFilterList = Array.from(venueFilter.value).sort();
    if (venueFilterList.length === 0) {
      updateQueryState({ venueFilter: null });
      return;
    }
    updateQueryState({ venueFilter: venueFilterList.join(',') });
  }

  function clearVenueFilter(): void {
    venueFilter.value.clear();
    updateQueryState({ venueFilter: null });
  }

  const awards = computed<string[]>(() => {
    if (allPapers.value == null) return [];
    const awardsSet = new Set<string>();
    for (const paper of allPapers.value) {
      for (const awardKey of getKeyList(paper.award)) {
        awardsSet.add(getAward(awardKey));
      }
    }
    awardsSet.delete('Unknown Award');
    return Array.from(awardsSet);
  });

  interface AwardCount {
    award: string;
    count: number;
  }
  const awardCounts = computed<AwardCount[]>(() => {
    const awardCountMap = new Map<string, number>();
    for (const award of awards.value) {
      awardCountMap.set(award, 0);
    }

    for (const paper of papers.value ?? []) {
      for (const awardKey of getKeyList(paper.award)) {
        const award = getAward(awardKey);
        awardCountMap.set(award, awardCountMap.get(award)! + 1);
      }
    }
    awardCountMap.delete('Unknown Award');

    const awardCountList: AwardCount[] = [];
    for (const [award, count] of awardCountMap.entries()) {
      awardCountList.push({ award, count });
    }

    const awardOrder = [
      getAward('TT'),
      getAward('BP'),
      getAward('HM'),
      getAward('BA'),
      getAward('BCS'),
    ];
    awardCountList.sort((a: AwardCount, b: AwardCount) => {
      return awardOrder.indexOf(a.award) - awardOrder.indexOf(b.award);
    });
    return awardCountList;
  });

  const maxAwardCount = computed<number>(() => {
    if (awardCounts.value.length === 0) return 0;
    return Math.max(
      ...awardCounts.value.map((awardCount: AwardCount) => awardCount.count)
    );
  });

  const awardFilter = ref<Set<string>>(
    new Set<string>(
      (currentRoute.value.query.awardFilter as string)?.split(',') ?? []
    )
  );

  function toggleAwardFilter(award: string): void {
    if (awardFilter.value.has(award)) {
      awardFilter.value.delete(award);
    } else {
      awardFilter.value.add(award);
    }
    const awardFilterList = Array.from(awardFilter.value).sort();
    if (awardFilterList.length === 0) {
      updateQueryState({ awardFilter: null });
      return;
    }
    updateQueryState({ awardFilter: awardFilterList.join(',') });
  }

  function clearAwardFilter(): void {
    awardFilter.value.clear();
    updateQueryState({ awardFilter: null });
  }

  const resources = computed<string[]>(() => {
    if (allPapers.value == null) return [];
    const resourcesSet = new Set<string>();
    for (const paper of allPapers.value) {
      for (const resourceKey of getKeyList(paper.resources)) {
        resourcesSet.add(resourceKey);
      }
    }
    return Array.from(resourcesSet);
  });

  interface ResourceCount {
    resource: string;
    count: number;
    key: string;
  }
  const resourceCounts = computed<ResourceCount[]>(() => {
    const resourceCountMap = new Map<string, number>();
    for (const resource of resources.value) {
      resourceCountMap.set(resource, 0);
    }

    for (const paper of papers.value ?? []) {
      for (const resourceKey of getKeyList(paper.resources)) {
        resourceCountMap.set(
          resourceKey,
          resourceCountMap.get(resourceKey)! + 1
        );
      }
    }

    const resourceCountList: ResourceCount[] = [];
    for (const [key, count] of resourceCountMap.entries()) {
      const resource = getResourceName(key);

      resourceCountList.push({ resource, count, key });
    }

    return resourceCountList;
  });

  const maxResourceCount = computed<number>(() => {
    if (resourceCounts.value.length === 0) return 0;
    return Math.max(
      ...resourceCounts.value.map(
        (resourceCount: ResourceCount) => resourceCount.count
      )
    );
  });

  const resourceFilter = ref<Set<string>>(
    new Set<string>(
      (currentRoute.value.query.resourceFilter as string)?.split(',') ?? []
    )
  );

  function toggleResourceFilter(resource: string): void {
    if (resourceFilter.value.has(resource)) {
      resourceFilter.value.delete(resource);
    } else {
      resourceFilter.value.add(resource);
    }
    const resourceFilterList = Array.from(resourceFilter.value).sort();
    if (resourceFilterList.length === 0) {
      updateQueryState({ resourceFilter: null });
      return;
    }
    updateQueryState({ resourceFilter: resourceFilterList.join(',') });
  }

  function clearResourceFilter(): void {
    resourceFilter.value.clear();
    updateQueryState({ resourceFilter: null });
  }

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
      updateQueryState({ matchCase: null });
      return;
    }
    updateQueryState({ matchCase: matchCase.value });
  });

  const useRegex = ref<string | null>(
    (currentRoute.value.query.useRegex as string) ?? null
  );
  watch(useRegex, () => {
    if (useRegex.value === null) {
      updateQueryState({ useRegex: null });
      return;
    }
    updateQueryState({ useRegex: useRegex.value });
  });

  const filterPanelOpen = ref<boolean>(
    currentRoute.value.query.filterPanelOpen === 'true'
  );

  watch(filterPanelOpen, () => {
    if (!filterPanelOpen.value) {
      updateQueryState({ filterPanelOpen: null });
      return;
    }
    updateQueryState({ filterPanelOpen: filterPanelOpen.value.toString() });
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
    searchFocused,
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
    paperYearCounts,
    maxPapersInYear,
    yearFilter,
    yearFilterSet,
    clearYearFilter,
    yearExtent,
    papersWithLinks,
    searchText,
    matchCase,
    useRegex,
    validRegex,
    regexErrorString,
    filterPanelOpen,
    venueCounts,
    maxVenueCount,
    venueFilter,
    toggleVenueFilter,
    clearVenueFilter,

    awardCounts,
    maxAwardCount,
    awardFilter,
    toggleAwardFilter,
    clearAwardFilter,

    resourceCounts,
    maxResourceCount,
    resourceFilter,
    toggleResourceFilter,
    clearResourceFilter,
  };
});
