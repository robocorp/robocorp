import { ChangeEvent, FC, FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { Button, Form, Header, Input } from '@robocorp/components';

import { runAction } from '~/lib/requestData';
import { Action, ActionPackage, AsyncLoaded } from '~/lib/types';
import { Code } from '~/components';

type Props = {
  action: Action;
  actionPackage: ActionPackage;
};

interface Value {
  type: string;
  description: string;
  title: string;
}

const dataLoadedInitial: AsyncLoaded<unknown> = {
  data: undefined,
  isPending: false,
};

const nameToUrl = (name: string): string => {
  return name.replaceAll('_', '-');
};

const convertType = (v: string, valueType: string): string | number | boolean => {
  switch (valueType) {
    case 'number':
      return parseFloat(v);
    case 'integer':
      return parseInt(v, 10);
    case 'boolean':
      if (v === 'false') {
        return false;
      }
      if (v === 'true') {
        return true;
      }
      throw new Error(`Unable to convert: ${v} to a boolean.`);
    case 'string':
    default:
      return v;
  }
};

type InputSchema = {
  required: string[];
  properties: Record<string, Value>;
};

export const ActionRun: FC<Props> = ({ action, actionPackage }) => {
  const inputSchema: InputSchema = useMemo(() => {
    return JSON.parse(action.input_schema);
  }, [action, actionPackage]);

  const properties: [string, Value][] = useMemo(() => {
    const found = inputSchema.properties;
    if (found === undefined) {
      return [];
    }
    return Object.entries(found);
  }, [action, actionPackage]);

  const [formData, setFormData] = useState<Record<string, string>>({});
  const [result, setResult] = useState<AsyncLoaded<unknown>>(dataLoadedInitial);

  useEffect(() => {
    if (inputSchema) {
      const { required } = inputSchema;
      const initialFormData = properties
        .filter(([key]) => required.includes(key))
        .map(([key, value]) => {
          switch (value.type) {
            case 'number':
              return [key, '0.0'];
            case 'boolean':
              return [key, 'true'];
            case 'integer':
              return [key, '0'];
            case 'string':
            default:
              return [key, ''];
          }
        });

      setFormData(Object.fromEntries(initialFormData));
    }
  }, [inputSchema, actionPackage, properties]);

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>, propertyName: string) => {
      const { value } = e.target;
      setFormData((curr) => {
        return {
          ...curr,
          [propertyName]: value,
        };
      });
      setResult(dataLoadedInitial);
    },
    [action, actionPackage, dataLoadedInitial, formData],
  );

  const fields = useMemo(() => {
    if (properties.length > 0) {
      const { required } = inputSchema;

      return properties.map(([key, value]) => {
        const isRequired = required.includes(key);
        const valueType = value.type;
        const { description } = value;
        let title = `${value.title} (${valueType})`;
        if (isRequired) {
          title += ' *';
        }

        if (valueType === 'string') {
          return (
            <Input
              key={key}
              label={title}
              rows={5}
              placeholder={undefined}
              description={description}
              value={formData[key]}
              onChange={(e) => handleInputChange(e, key)}
            />
          );
        }

        return (
          <Input
            key={key}
            label={title}
            placeholder={undefined}
            description={description}
            value={formData[key]}
            onChange={(e) => handleInputChange(e, key)}
          />
        );
      });
    }

    return [];
  }, [action, actionPackage, inputSchema, handleInputChange, properties]);

  const onSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();

      const useData = Object.entries(formData).map(([key, value]) => {
        const valueType = inputSchema.properties[key].type;
        return [key, convertType(value, valueType)];
      });

      if (action?.name && actionPackage?.name) {
        runAction(
          nameToUrl(actionPackage.name),
          nameToUrl(action.name),
          Object.fromEntries(useData),
          setResult,
        );
      }
    },
    [formData, action, actionPackage, inputSchema, result, setResult],
  );

  return (
    <Form busy={result.isPending} onSubmit={onSubmit}>
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
          <Code lineNumbers={false} value={result.errorMessage || (result.data as string)} />
        </>
      )}
    </Form>
  );
};
