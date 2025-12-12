import { DropZone, DropZoneProps } from '@snack-uikit/drop-zone';
import { useCallback } from 'react';
import { Typography } from '@snack-uikit/typography';
import { useMobxStore } from '#app/store/context';

import styles from './fileRequirements.module.scss';

export const FileRequirements = () => {
  const { testSettings } = useMobxStore();
  const { changeTestSettings, fileRequirements } = testSettings;

  const onFilesUpload = useCallback<DropZoneProps['onFilesUpload']>((files: File[]) => {
    const [value] = files;
    changeTestSettings({ key: 'fileRequirements', value });
  }, []);

  return (
    <>
      <DropZone
        mode='single'
        description='Прикрепите требования в формате PDF, TXT или DOCX'
        onFilesUpload={onFilesUpload}
        className={styles.file}
      />
      {fileRequirements && (
        <ul className={styles.desc}>
          <li>
            <Typography.SansTitleS tag='span'>Название файла: </Typography.SansTitleS>
            <Typography.SansBodyS>{fileRequirements?.name}</Typography.SansBodyS>
          </li>
          <li>
            <Typography.SansTitleS tag='span'>Тип файла: </Typography.SansTitleS>
            <Typography.SansBodyS>{fileRequirements?.type}</Typography.SansBodyS>
          </li>
        </ul>
      )}
    </>
  );
};
