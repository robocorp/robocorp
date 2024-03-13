import { ChangeEvent, FC, FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { Button, Checkbox, Form, Input } from '@robocorp/components';

import { Action, ActionPackage, InputProperty, InputPropertyType } from '~/lib/types';
import { useActionServerContext } from '~/lib/actionServerContext';
import { useLocalStorage } from '~/lib/useLocalStorage';
import { useActionRunMutation } from '~/queries/actions';
import { toKebabCase } from '~/lib/helpers';
import { ActionRunResult } from './ActionRunResult';

type Props = {
  action: Action;
  actionPackage: ActionPackage;
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
  const { mutate: runAction, isPending, isSuccess, data, reset } = useActionRunMutation();

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
      reset();
    },
    [action, actionPackage, formData],
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

      runAction({
        actionPackageName: toKebabCase(actionPackage.name),
        actionName: toKebabCase(action.name),
        args: Object.fromEntries(useData),
        apiKey: serverConfig?.auth_enabled ? apiKey : undefined,
      });
    },
    [formData, action, actionPackage, serverConfig, apiKey],
  );

  return (
    <Form busy={isPending} onSubmit={onSubmit}>
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
        <Button loading={isPending} type="submit" variant="primary">
          Run
        </Button>
      </Button.Group>
      {isSuccess && <ActionRunResult result={data.response} runId={data.runId} />}
    </Form>
  );
};
