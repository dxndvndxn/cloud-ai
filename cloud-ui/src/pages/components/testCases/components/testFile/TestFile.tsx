import { CodeEditor, CodeEditorProps } from '@snack-uikit/code-editor';
import { useMobxStore } from '#app/store/context';
import { observer } from 'mobx-react-lite';
import styles from './testFile.module.scss';
import { TestCaseBlock } from '../testCaseBlock';
import { TestNoData } from '../testNoData';
import { Skeleton } from '@snack-uikit/skeleton';

const options: CodeEditorProps['options'] = {
  scrollbar: {
    vertical: 'visible', // Options: 'auto', 'visible', 'hidden'
    horizontal: 'visible', // Options: 'auto', 'visible', 'hidden'
    verticalScrollbarSize: 15, // Width in pixels
    horizontalScrollbarSize: 15, // Height in pixels
  },
};

export const TestFile = observer(() => {
  const { testCases, testSettings } = useMobxStore();
  const { selectedFile, selectedFileName, directory_structure } = testCases;

  return (
    <TestCaseBlock label={`Файл ${selectedFileName}`} className={styles.file}>
      <Skeleton className={styles.fileSkeleton} borderRadius={16} loading={testSettings.loading && !directory_structure}>
        {!directory_structure && <TestNoData />}
        {!!directory_structure && (
          <CodeEditor options={options} className={styles.editor} hasHeader language='python' value={selectedFile} />
        )}
      </Skeleton>
    </TestCaseBlock>
  );
});

