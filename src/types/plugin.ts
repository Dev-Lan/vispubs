export interface PluginPaper {
  doi: string;
  title: string;
  year: number;
  conference: string;
  award: string;
  authorNamesDeduped: string;
  abstract: string;
  resources?: string;
  accessible: boolean;
  early: boolean;
}

export interface PluginFilterState {
  searchText: string;
  matchCase: boolean;
  useRegex: boolean;
  yearFilter: { min: number; max: number } | null;
  venueFilter: string[];
  awardFilter: string[];
  resourceFilter: string[];
  collection: string | null;
}

export interface PluginStatePayload {
  type: 'vispubs:state';
  papers: PluginPaper[];
  filters: PluginFilterState;
  selectedDoi: string | null;
  focusedDoi: string | null;
  darkMode: boolean;
}

export type HostToPluginMessage = PluginStatePayload;

export interface PluginReadyMessage {
  type: 'vispubs:ready';
}

export interface PluginSelectPaperMessage {
  type: 'vispubs:selectPaper';
  doi: string;
}

export interface PluginFocusPaperMessage {
  type: 'vispubs:focusPaper';
  doi: string | null;
}

export type PluginToHostMessage =
  | PluginReadyMessage
  | PluginSelectPaperMessage
  | PluginFocusPaperMessage;

export const VISPUBS_MESSAGE_PREFIX = 'vispubs:';
