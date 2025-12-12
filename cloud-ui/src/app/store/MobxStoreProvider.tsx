import { ComponentType, useState } from 'react';

import { MobxStoreContext } from './context';

import { initializeStore } from './initializeStore';

export function withWithMobxStoreProvider(Component: ComponentType) {
  return function WithMobxStoreProvider() {
    const [store] = useState(() => initializeStore());
    return (
      <MobxStoreContext.Provider value={store}>
        <Component />
      </MobxStoreContext.Provider>
    );
  };
}
