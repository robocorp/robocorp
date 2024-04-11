/* eslint-disable react/no-array-index-key */
import { FC, FormEvent, ReactNode, useCallback, useEffect, useState } from 'react';
import {
  Box,
  Button,
  Checkbox,
  Divider,
  Form,
  Input,
  Select,
  Switch,
  Typography,
} from '@robocorp/components';
import { IconBolt } from '@robocorp/icons/iconic';

import { Action, ActionPackage } from '~/lib/types';
import { toKebabCase } from '~/lib/helpers';
import { useActionServerContext } from '~/lib/actionServerContext';
import { useLocalStorage } from '~/lib/useLocalStorage';
import {
  formDataToPayload,
  Payload,
  payloadToFormData,
  propertiesToFormData,
  PropertyFormData,
  PropertyFormDataType,
} from '~/lib/formData';
import { useActionRunMutation } from '~/queries/actions';
import { Code } from '~/components/Code';
import { ActionRunResult } from './ActionRunResult';

type Props = {
  action: Action;
  actionPackage: ActionPackage;
};

const Item: FC<{ children?: ReactNode; title?: string; name: string }> = ({
  children,
  title,
  name,
}) => {
  const indent = name.split('.').length - 1;
  return (
    <Box pl={indent * 8}>
      {title && (
        <Typography mb="$8" variant="display.small">
          {title}
        </Typography>
      )}
      {children}
    </Box>
  );
};

const ItemArray: FC<{ children?: ReactNode; title?: string; name: string }> = ({
  children,
  title,
  name,
}) => {
  const indent = name.split('.').length - 2;
  return (
    <Box display="flex" justifyContent="space-between" pl={indent * 16}>
      <Typography mb="$8" variant="display.small">
        {title}
      </Typography>
      {children}
    </Box>
  );
};

export const ActionRun: FC<Props> = ({ action, actionPackage }) => {
  const [apiKey, setApiKey] = useLocalStorage<string>('api-key', '');
  const { serverConfig } = useActionServerContext();
  const { mutate: runAction, isPending, isSuccess, data, reset } = useActionRunMutation();
  const [formData, setFormData] = useState<PropertyFormData[]>([]);
  const [useRawJSON, setUseRawJSON] = useState<boolean>(false);
  const [formRawJSON, setFormRawJSON] = useState<string>('');
  const [errorJSON, setErrorJSON] = useState<string>();

  useEffect(() => {
    setFormData(propertiesToFormData(JSON.parse(action.input_schema)));
  }, [action, actionPackage]);

  const handleInputChange = useCallback((value: PropertyFormDataType, index: number) => {
    setFormData((curr) => curr.map((item, idx) => (idx === index ? { ...item, value } : item)));
    reset();
  }, []);

  const onAddRow = (index: number) => {
    setFormData((curr) => {
      let row: PropertyFormData[] = JSON.parse(JSON.stringify(curr[index].value));

      const depth = curr[index].name.split('.').length + 1;

      const lastIndex =
        curr
          .findLast((item) => item.name.startsWith(curr[index].name))
          ?.name.split('.')
          .slice(depth - 1)[0] || '0';

      const newIndex = parseInt(lastIndex, 10) + 1;

      row = row.map((item) => {
        const suffix = item.name.split('.').slice(depth).join('.');
        const newName = `${curr[index].name}.${newIndex}${suffix ? `.${suffix}` : suffix}`;

        return {
          ...item,
          name: newName,
        };
      });

      let indexAt = index + 1;

      for (let i = index; i <= curr.length - 1; i += 1) {
        if (curr[i].name.startsWith(curr[index].name)) {
          indexAt = i + 1;
        } else {
          break;
        }
      }

      if (Array.isArray(row)) {
        return [...curr.slice(0, indexAt), ...row, ...curr.slice(indexAt)];
      }

      return curr;
    });
  };

  const onSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();

      runAction({
        actionPackageName: toKebabCase(actionPackage.name),
        actionName: toKebabCase(action.name),
        args: useRawJSON ? JSON.parse(formRawJSON) : formDataToPayload(formData),
        apiKey: serverConfig?.auth_enabled ? apiKey : undefined,
      });
    },
    [action, actionPackage, formData, apiKey, serverConfig, useRawJSON, formRawJSON],
  );

  const onCodeChange = useCallback(
    (value: string) => {
      setFormRawJSON(value);
      try {
        JSON.parse(value) as Payload;
        setErrorJSON(undefined);
      } catch (_) {
        setErrorJSON('Error while parsing JSON. Please review value and try again');
      }
    },
    [setFormRawJSON, setErrorJSON],
  );

  useEffect(() => {
    setFormData(propertiesToFormData(JSON.parse(action.input_schema)));
  }, [action, actionPackage]);

  useEffect(() => {
    if (!useRawJSON) {
      try {
        setFormData(payloadToFormData(JSON.parse(formRawJSON), formData));
      } catch (err) {
        setFormRawJSON('Bad input data...');
      }
    } else {
      try {
        if (formData.length === 0) {
          setFormRawJSON('No input data...');
        } else {
          const payload = formDataToPayload(formData);
          setFormRawJSON(JSON.stringify(payload, null, 4));
        }
      } catch (err) {
        setFormRawJSON('Bad input data...');
      }
    }
  }, [useRawJSON]);

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
      {useRawJSON ? (
        <Code
          key="form-raw-json-input"
          lang="json"
          aria-label="Run JSON input"
          value={formRawJSON}
          onChange={onCodeChange}
          error={errorJSON}
          readOnly={false}
          lineNumbers
          autoFocus
        />
      ) : (
        <Form.Fieldset key="form-field-sets">
          {formData.map((item, index) => {
            const title = `${item.property.title}${item.required ? ' *' : ''}`;

            switch (item.property.type) {
              case 'boolean':
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Checkbox
                      key={`${title}-${item.name}-${index}`}
                      label={title}
                      description={item.property.description}
                      checked={typeof item.value === 'boolean' && item.value}
                      required={item.required}
                      onChange={(e) => handleInputChange(e.target.checked, index)}
                    />
                  </Item>
                );
              case 'number':
              case 'integer':
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Input
                      key={`${title}-${item.name}-${index}`}
                      label={title}
                      description={item.property.description}
                      required={item.required}
                      value={typeof item.value === 'number' ? item.value.toString() : '0'}
                      type="number"
                      onChange={(e) => handleInputChange(parseInt(e.target.value, 10), index)}
                    />
                  </Item>
                );
              case 'object':
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Input
                      key={`${title}-${item.name}-${index}`}
                      label={title}
                      description={item.property.description}
                      required={item.required}
                      value={typeof item.value === 'object' ? JSON.stringify(item.value) : '{}'}
                      rows={4}
                      onChange={(e) => handleInputChange(e.target.value, index)}
                    />
                  </Item>
                );
              case 'enum':
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Select
                      key={`${title}-${item.name}-${index}`}
                      label={title}
                      description={item.property.description}
                      required={item.required}
                      value={
                        typeof item.value === 'string' ? item.value : JSON.stringify(item.value)
                      }
                      items={item.options?.map((value) => ({ label: value, value })) || []}
                      onChange={(e) => handleInputChange(e, index)}
                    />
                  </Item>
                );
              case 'array':
                return (
                  <ItemArray title={item.title} name={item.name} key={item.name}>
                    <Button type="button" onClick={() => onAddRow(index)} size="small">
                      Add row
                    </Button>
                  </ItemArray>
                );
              case 'string':
              default:
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Input
                      key={`${item.title}-${item.name}-${index}`}
                      label={item.title}
                      description={item.property.description}
                      rows={1}
                      required={item.required}
                      value={
                        typeof item.value === 'string' ? item.value : JSON.stringify(item.value)
                      }
                      onChange={(e) => handleInputChange(e.target.value, index)}
                    />
                  </Item>
                );
            }
          })}
        </Form.Fieldset>
      )}
      <Button.Group align="right" marginBottom={isSuccess ? 16 : 32} justifyContent="space-between">
        <Button
          loading={isPending}
          type="submit"
          variant="primary"
          icon={IconBolt}
          style={{ width: '160px' }}
          disabled={errorJSON !== undefined}
        >
          {isPending ? 'Executing...' : 'Execute Action'}
        </Button>
        <Switch
          label=""
          value="Use JSON"
          checked={useRawJSON}
          onChange={(e) => setUseRawJSON(e.target.checked)}
        />
      </Button.Group>
      <Divider />
      {isSuccess && (
        <ActionRunResult
          result={data.response}
          runId={data.runId}
          outputSchemaType={JSON.parse(action.output_schema) as { type: string }}
        />
      )}
    </Form>
  );
};
