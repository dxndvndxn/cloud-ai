import { TestSettingsStore } from '#pages/components/testSettings/store';
import { TestCasesStore } from '#pages/components/testCases/store/TestCasesStore';
import type { StoreModal } from './context';

let store: StoreModal | null = null;

export const initializeStore = (): StoreModal => {
  const initialStore = store ?? {
    testSettings: new TestSettingsStore(),
    testCases: new TestCasesStore(),
  };

  // Только в dev-режиме: не кэшируем store при hot-reload
  if (typeof window === 'undefined') return initialStore;
  if (store === null) store = initialStore;

  return store;
};
