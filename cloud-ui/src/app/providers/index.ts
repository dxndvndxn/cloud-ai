import { ComponentType } from 'react';

import { withLocale } from './withLocale';
import { withWithMobxStoreProvider } from '../store';

export function withProviders(Component: ComponentType) {
  return [withLocale, withWithMobxStoreProvider].reduceRight((Target, wrap) => wrap(Target), Component);
}
