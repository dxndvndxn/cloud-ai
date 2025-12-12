import { Tabs } from '@snack-uikit/tabs';
import { UiTestInputs, ApiTestInputs, ChatRequirements } from './components';
import { Typography } from '@snack-uikit/typography';
import { Divider } from '@snack-uikit/divider';
import { useMobxStore } from '#app/store/context';
import type { CaseType } from './store/TestSettingsStore';
import { observer } from 'mobx-react-lite';

import styles from './testSettings.module.scss';
import cn from 'classnames';

const { TabBar, Tab, TabContent } = Tabs;

export const TestSettings = observer(() => {
  const { testSettings } = useMobxStore();
  const { changeTestSettings, caseType } = testSettings;

  const onChangeTab = (caseType: CaseType) => {
    changeTestSettings({ key: 'caseType', value: caseType });
  };

  return (
    <div className={styles.sideControl}>
      <div className={styles.settings}>
        <Tabs value={caseType} onChange={onChangeTab}>
          <TabBar className={styles.mB20}>
            <Tab label='UI тесты' value='ui' />
            <Tab label='API тесты' value='api' />
          </TabBar>

          <div className={cn(styles.inputs, styles.mB20)}>
            <TabContent value='ui'>
              <UiTestInputs />
            </TabContent>
            <TabContent className={styles.inputs} value='api'>
              <ApiTestInputs />
            </TabContent>
          </div>

          <Divider className={styles.divider} />

          <Typography.SansTitleM className={styles.mB20} tag='h1'>
            Укажите требования
          </Typography.SansTitleM>

        </Tabs>
      </div>

      <div className={styles.text}>
        <ChatRequirements />
      </div>
    </div>
  );
});
