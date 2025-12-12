import { http } from '#shared/http';
import { FieldTextArea, type FieldTextAreaProps } from '@snack-uikit/fields';
import { useCallback, useLayoutEffect, useRef } from 'react';
import { ButtonFilled } from '@snack-uikit/button';
import { useMobxStore } from '#app/store/context';
import { observer } from 'mobx-react-lite';

import styles from './chatRequirements.module.scss';
import type { CaseType } from '../../store/TestSettingsStore';
import type { CreateTestCaseResponse } from '../../../../types';
import { toaster } from '@snack-uikit/toaster';

export const ChatRequirements = observer(() => {
  const textRef = useRef<HTMLTextAreaElement>(null);
  const heightChat = useRef<Record<CaseType, number>>({} as any)

  const { testSettings, testCases } = useMobxStore();
  const { changeTestSettings, tags, text, base_endpoint, ui_url, token, caseType } = testSettings;
  const { clearCases } = testCases;

  const changeText = useCallback<onBlurCallback>(({ target }) => {
    changeTestSettings({ key: 'text', value: target.value });
  }, []);

  const sendRequirementsByUi = useCallback(async () => {
    return await http<CreateTestCaseResponse>({
      api: 'ui_agent_entry_point',
      method: 'POST',
      body: {
        text,
        ui_url,
      },
    });
  }, [text, ui_url]);

  const sendRequirementsByApi = useCallback(async () => {
    return await http<CreateTestCaseResponse>({
      api: 'api_agent_entry_point',
      method: 'POST',
      body: {
        text,
        tags,
        base_endpoint,
        token,
      },
    });
  }, [text, tags, base_endpoint, token]);

  const sendRequirements = useCallback(async () => {
    try {
      changeTestSettings({ key: 'loading', value: true });
      clearCases();
      let response;

      if (caseType === 'api') {
        response = await sendRequirementsByApi();
      } else {
        response = await sendRequirementsByUi();
      }

      if ((response as CreateTestCaseResponse)?.success) {
        await toaster.systemEvent.success({
          title: 'Success',
          description: 'Тесты успешно сгенирировались',
        });
      } else {
        await toaster.systemEvent.error({
          title: 'Error',
          description: 'Тесты не сгенирировались',
        });
      }
    } catch (e) {
      console.log(e);
    } finally {
      changeTestSettings({ key: 'loading', value: false });
    }
  }, [sendRequirementsByApi, sendRequirementsByUi, caseType]);

  useLayoutEffect(() => {
    if (textRef.current) {
      let height;
      if (heightChat.current?.[caseType]) {
        height = heightChat.current?.[caseType];
      } else {
        heightChat.current[caseType] = (textRef.current.parentNode?.parentNode?.parentNode as HTMLDivElement)?.clientHeight;
        height = heightChat.current[caseType]
      }

      (textRef?.current.parentNode?.parentNode as HTMLDivElement).style.maxHeight = `${height}px`;
    }
  }, [caseType]);

  return (
    <>

      <FieldTextArea
        ref={textRef}
        size='l'
        minRows={10}
        maxRows={10}
        className={styles.chat}
        onBlur={changeText}
      ></FieldTextArea>

      <div className={styles.send}>
        <ButtonFilled
          disabled={testSettings.loading}
          loading={testSettings.loading}
          label='Отправить'
          size='m'
          appearance='primary'
          onClick={sendRequirements}
        />
      </div>
    </>
  );
});

type onBlurCallback = NonNullable<FieldTextAreaProps['onBlur']>;
