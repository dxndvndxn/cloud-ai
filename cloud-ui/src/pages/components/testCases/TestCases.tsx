import React, { useCallback, useEffect, useState } from 'react';
import type { TestCasesWS } from '../../types';
import { TestPlan, TestFile, TestFileStructure } from './components';
import { TestCaseBlock } from './components/testCaseBlock';
import { useMobxStore } from '#app/store/context';

import styles from './testCases.module.scss';
import { Divider } from '@snack-uikit/divider';
import { toaster } from '@snack-uikit/toaster';

export const TestCases = () => {
  const [testCasesWs, setTestCasesWs] = useState<WebSocket>();
  const { testCases } = useMobxStore();
  const { setTestCases } = testCases;

  const setWebSocketConnect = useCallback(() => {
    const newChat = new WebSocket(`ws://${import.meta.env.VITE_APP_API}/api/v1/ws`);
    const showErrorNotification = async (description?: string) => {

      const id =  await toaster.systemEvent.error({
        title: 'Ошибка соединения',
        description,
        action: [{
          label: 'Подключить соединение заново?',
          onClick() {
            setTestCasesWs(undefined);
            toaster.systemEvent.dismiss(id);
          }
        }]
      });

      return;
    }

    newChat.onopen = () => {
      toaster.systemEvent.success({
        title: 'Success',
        description: 'Успешное соединение с сервером',
      });
      console.log('open');
    };

    newChat.onmessage = (event: MessageEvent<string>) => {
      const response = (event.data ? JSON.parse(event.data) : {}) as TestCasesWS;

      console.log('response', response);

      if (response.type === 'error') {
        return showErrorNotification(response.message);
      }
      if (response.status) {
        toaster.systemEvent.neutral({
          title: 'Статус генерации',
          description: response.status,
        });
      }

      setTestCases(response);
    };

    newChat.onclose = event => {
      console.log('onclose', event);
      newChat.close();
      return showErrorNotification('Соединение разорорвано');
    };

    newChat.onerror = error => {
      console.error('onerror', error);
      newChat.close();
    };

    setTestCasesWs(newChat)
  }, [])

  useEffect(() => {
    if (!testCasesWs) setWebSocketConnect();
  }, [testCasesWs]);

  return (
    <div className={styles.grid}>
      <div className={styles.col}>
        <TestCaseBlock label='План тестирования' className={styles.plan}>
          <TestPlan />
        </TestCaseBlock>
        <Divider orientation='horizontal'/>
        <TestCaseBlock label='Каталог' className={styles.structure}>
          <TestFileStructure />
        </TestCaseBlock>
      </div>

      <Divider orientation='vertical'/>

      <div className={styles.col}>
        <TestFile />
      </div>
    </div>
  );
};
