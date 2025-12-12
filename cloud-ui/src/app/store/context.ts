import { createContext, useContext } from 'react';
import { TestSettingsStore } from '#pages/components/testSettings/store';
import { TestCasesStore } from '#pages/components/testCases/store/TestCasesStore';

export interface StoreModal {
  testSettings: TestSettingsStore;
  testCases: TestCasesStore;
}

export const MobxStoreContext = createContext<StoreModal | null>(null);

export const useMobxStore = () => {
  const store = useContext(MobxStoreContext);

  if (!store) {
    throw new Error('useMobxStore must be used within MobxStoreProvider');
  }

  return store;
};
