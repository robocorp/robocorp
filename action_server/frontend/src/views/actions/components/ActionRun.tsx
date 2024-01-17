import { ChangeEvent, FC, FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { Button, Checkbox, Form, Header, Input } from '@robocorp/components';

import { runAction } from '~/lib/requestData';
import { Action, ActionPackage, AsyncLoaded, InputProperty, InputPropertyType } from '~/lib/types';
import { Code } from '~/components';
import { stringifyResult } from '~/lib/helpers';
import { useActionServerContext } from '~/lib/actionServerContext';
import { useLocalStorage } from '~/lib/useLocalStorage';

type Props = {
  action: Action;
  actionPackage: ActionPackage;
};

type RunResult = string | number | boolean | undefined;

const dataLoadedInitial: AsyncLoaded<RunResult> = {
  data: undefined,
  isPending: false,
};

const nameToUrl = (name: string): string => {
  return name.replaceAll('_', '-');
};

const convertType = (v: string, valueType: InputPropertyType): string | number | boolean => {
  switch (valueType) {
    case InputPropertyType.NUMBER:
      return parseFloat(v);
    case InputPropertyType.INTEGER:
      return parseInt(v, 10);
    case InputPropertyType.BOOLEAN:
      if (v === 'False') {
        return false;
      }
      if (v === 'True') {
        return true;
      }
      throw new Error(`Unable to convert: ${v} to a boolean.`);
    case InputPropertyType.STRING:
    default:
      return v;
  }
};

type InputSchema = {
  required: string[] | undefined; // May be undefined if there are no required entries.
  properties: Record<string, InputProperty>;
};

type FormDataEntry = [string, InputProperty, string];

export const ActionRun: FC<Props> = ({ action, actionPackage }) => {
  const [apiKey, setApiKey] = useLocalStorage<string>('api-key', '');
  const { serverConfig } = useActionServerContext();
  const [formData, setFormData] = useState<FormDataEntry[]>([]);
  const [result, setResult] = useState<AsyncLoaded<RunResult>>(dataLoadedInitial);

  const inputSchema: InputSchema = useMemo(() => {
    return JSON.parse(action.input_schema);
  }, [action, actionPackage]);

  useEffect(() => {
    if (inputSchema.properties) {
      const initialFormData = Object.entries(inputSchema.properties).map<FormDataEntry>(
        ([key, value]) => {
          if (value.default) {
            return [key, value, value.default];
          }

          switch (value.type) {
            case InputPropertyType.NUMBER:
              return [key, value, '0.0'];
            case InputPropertyType.BOOLEAN:
              return [key, value, 'True'];
            case InputPropertyType.INTEGER:
              return [key, value, '0'];
            case InputPropertyType.STRING:
            default:
              return [key, value, ''];
          }
        },
      );

      setFormData(initialFormData);
    }
  }, [inputSchema, actionPackage]);

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>, index: number) => {
      setFormData((curr) => {
        const output = [...curr];
        const [, field] = output[index];

        if (field.type === InputPropertyType.BOOLEAN) {
          output[index][2] = e.target.checked ? 'True' : 'False';
        } else {
          output[index][2] = e.target.value;
        }
        return output;
      });
      setResult(dataLoadedInitial);
    },
    [action, actionPackage, dataLoadedInitial, formData],
  );

  const fields = useMemo(() => {
    const { required } = inputSchema;

    return formData.map(([key, property, value], index) => {
      const isRequired = required && required.includes(key);
      const { description } = property;
      const title = `${property.title}${isRequired ? ' *' : ''}`;

      switch (property.type) {
        case InputPropertyType.NUMBER:
        case InputPropertyType.INTEGER:
          return (
            <Input
              key={key}
              label={title}
              description={description}
              value={value}
              type="number"
              required={isRequired}
              onChange={(e) => handleInputChange(e, index)}
            />
          );
        case InputPropertyType.BOOLEAN:
          return (
            <Checkbox
              key={key}
              label={title}
              description={description}
              checked={value === 'True'}
              required={isRequired}
              onChange={(e) => handleInputChange(e, index)}
            />
          );
        case InputPropertyType.STRING:
        default:
          return (
            <Input
              key={key}
              label={title}
              description={description}
              rows={2}
              required={isRequired}
              value={value}
              onChange={(e) => handleInputChange(e, index)}
            />
          );
      }
    });
  }, [action, actionPackage, inputSchema, handleInputChange]);

  const onSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();

      const useData = formData.map(([key, field, value]) => {
        return [key, convertType(value, field.type)];
      });

      if (action?.name && actionPackage?.name) {
        runAction(
          nameToUrl(actionPackage.name),
          nameToUrl(action.name),
          Object.fromEntries(useData),
          setResult,
          serverConfig?.auth_enabled ? apiKey : undefined,
        );
      }
    },
    [formData, action, actionPackage, inputSchema, result, serverConfig, apiKey, setResult],
  );

  return (
    <Form busy={result.isPending} onSubmit={onSubmit}>
      {serverConfig?.auth_enabled && (
        <Form.Fieldset>
          <Input
            label="API Key"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
        </Form.Fieldset>
      )}
      <Form.Fieldset>{fields}</Form.Fieldset>
      <Button.Group align="right">
        <Button loading={result.isPending} type="submit" variant="primary">
          Run
        </Button>
      </Button.Group>
      {!result.isPending && (result.data !== undefined || result.errorMessage) && (
        <>
          <Header size="small">
            <Header.Title title="Result" />
          </Header>
          <Code lineNumbers={false} value={result.errorMessage || stringifyResult(result.data)} />
        </>
      )}
    </Form>
  );
};
