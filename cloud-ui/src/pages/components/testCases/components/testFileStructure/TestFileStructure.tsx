import { Tree } from '@snack-uikit/tree';
import { useMobxStore } from '#app/store/context';
import { observer } from 'mobx-react-lite';
import { useCallback, useMemo, useState } from 'react';
import { structureFilesAdapter } from '../../utils';
import type { SelectFileArgs } from '../../store';
import styles from './testFileStructure.module.scss';
import { ButtonFilled } from '@snack-uikit/button';
import { http } from '#shared/http';
import { Scroll } from '@snack-uikit/scroll';
import { TestNoData } from '../testNoData';
import { Skeleton } from '@snack-uikit/skeleton';

export const TestFileStructure = observer(() => {
  const [loading, setLoading] = useState(false);

  const { testCases, testSettings } = useMobxStore();
  const { directory_structure, selectFile } = testCases;

  const setActiveFile = useCallback((selectedData: SelectFileArgs) => {
    selectFile(selectedData);
  }, []);

  const data = useMemo(() => {
    if (!directory_structure) return [];

    return structureFilesAdapter(directory_structure, setActiveFile);
  }, [directory_structure]);

  const startTest = async () => {
    try {
      setLoading(true);
      const blob = await http<any>({ api: 'play_tests', method: 'POST', isFile: true });
      const url = window.URL.createObjectURL(blob); // Создаем URL для Blob
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = 'tests.zip'; // Имя файла для скачивания
      document.body.appendChild(a);
      a.click(); // Имитируем клик по ссылке
      window.URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Scroll barHideStrategy='never'>
        <Skeleton height='100%' borderRadius={16} loading={testSettings.loading && !data.length}>
          {!data.length && <TestNoData />}

          <Tree
            data={data}
            selectionMode='single'
            onNodeClick={(node, e) => {
              if (node?.onClick) {
                node.onClick(e);
              }
            }}
          />
        </Skeleton>
      </Scroll>

      {!!data.length && (
        <div className={styles.send}>
          <ButtonFilled
            disabled={testSettings.loading || loading}
            loading={loading}
            label='Скачать'
            size='m'
            appearance='primary'
            onClick={startTest}
          />
        </div>
      )}
    </>
  );
});
