import { useCallback } from 'react';
import { FieldText, type FieldTextProps } from '@snack-uikit/fields';
import { useMobxStore } from '#app/store/context';

export const UiTestInputs = () => {
  const { testSettings } = useMobxStore();
  const { changeTestSettings } = testSettings;

  const changeUiUrl = useCallback<onBlurCallback>(({ target }) => {
    changeTestSettings({ key: 'ui_url', value: target.value });
  }, []);

  return <FieldText required label='Url для тестирования' inputMode='text' onBlur={changeUiUrl} />;
};

type onBlurCallback = NonNullable<FieldTextProps['onBlur']>;
