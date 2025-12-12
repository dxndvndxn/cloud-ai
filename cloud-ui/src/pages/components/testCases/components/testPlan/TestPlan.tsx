import { Markdown } from '@snack-uikit/markdown';
import { useMobxStore } from '#app/store/context';
import { observer } from 'mobx-react-lite';
import { TestNoData } from '../testNoData';
import { Skeleton } from '@snack-uikit/skeleton';
import styles from './testPlan.module.scss';

export const TestPlan = observer(() => {
  const { testCases, testSettings } = useMobxStore();
  const { test_plan } = testCases;

  return (
    <div className={styles.wrapPlan}>
      <Skeleton height='100%' borderRadius={16} loading={testSettings.loading && !test_plan?.length}>
        {!test_plan?.length && <TestNoData />}
        <Markdown className={styles.mark} value={test_plan} />
      </Skeleton>
    </div>
  );
});
