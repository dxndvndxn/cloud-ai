import { makeAutoObservable } from 'mobx';

export type CaseType = 'ui' | 'api';

export class TestSettingsStore {
  text = '';
  caseType: CaseType = 'ui';
  loading = false;
  tags?: string[] = ['VMs'];
  base_endpoint?: string = '';
  token?: string = '';
  ui_url?: string = '';
  fileRequirements?: File;

  constructor() {
    makeAutoObservable(this);
  }

  changeTestSettings = <K extends keyof TestSettingsStore>({ key, value }: { key: K; value: TestSettingsStore[K] }) => {
    (this as TestSettingsStore)[key] = value;
  };
}
