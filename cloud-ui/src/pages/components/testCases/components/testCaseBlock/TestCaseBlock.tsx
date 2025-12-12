import { Typography } from '@snack-uikit/typography';
import styles from './testCaseBlock.module.scss';
import { PropsWithChildren } from 'react';

export interface TestCaseBlockProps extends PropsWithChildren {
  label: string;
  className?: string;
}

export const TestCaseBlock = ({ label, className, children }: TestCaseBlockProps) => {
  return (
    <div className={className}>
      <Typography.SansTitleM className={styles.label} tag='h1'>
        {label}
      </Typography.SansTitleM>

      {children}
    </div>
  );
};
