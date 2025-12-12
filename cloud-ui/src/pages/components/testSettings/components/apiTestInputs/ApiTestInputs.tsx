import { useCallback } from 'react';
import { FieldSelect, FieldText, type FieldTextProps, type FieldSelectProps } from '@snack-uikit/fields';
import { useMobxStore } from '#app/store/context';
import { tagsOptions } from './constants';
import { observer } from 'mobx-react-lite';

export const ApiTestInputs = observer(() => {
  const { testSettings } = useMobxStore();
  const { changeTestSettings, tags } = testSettings;

  const changeEndpoint = useCallback<onBlurCallback>(({ target }) => {
    changeTestSettings({ key: 'base_endpoint', value: target.value });
  }, []);

  const changeOpenapi = useCallback<onChangeOpenApiCallback>(value => {
    changeTestSettings({ key: 'tags', value });
  }, []);

  const changeToken = useCallback<onBlurCallback>(({ target }) => {
    changeTestSettings({ key: 'token', value: target.value });
  }, []);

  return (
    <>
      <FieldText
        required
        label='Endpoint'
        inputMode='text'
        onBlur={changeEndpoint}
      />
      <FieldSelect
        required
        selection='multiple'
        value={tags}
        onChange={changeOpenapi}
        options={tagsOptions}
        id='tags'
        name='tags'
        label='Разделы OpenAPI'
        searchable={true}
        enableFuzzySearch={true}
      />
      <FieldText required label='Token' inputMode='text' onBlur={changeToken} />
    </>
  );
});

type onBlurCallback = NonNullable<FieldTextProps['onBlur']>;
type onChangeOpenApiCallback = NonNullable<FieldSelectProps['onChange']>;
