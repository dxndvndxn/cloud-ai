import styles from './testNoData.module.scss';
import { Typography } from '@snack-uikit/typography';

export const TestNoData = () => {
  return (
    <div className={styles.noData}>
      <Typography.SansTitleL>Нет данных</Typography.SansTitleL>
    </div>
  );
};
