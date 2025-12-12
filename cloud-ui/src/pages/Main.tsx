import { TestSettings } from './components';
import { TestCases } from './components/testCases';
import { Divider } from '@snack-uikit/divider';

import styles from './main.module.scss';

export const Main = () => {
  return (
    <div className={styles.wrapper}>
      <TestSettings />
      <Divider orientation='vertical' className={styles.divider} />
      <TestCases />
    </div>
  );
};
