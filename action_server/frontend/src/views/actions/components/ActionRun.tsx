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
import { logError, toKebabCase } from '~/lib/helpers';
import { useActionServerContext } from '~/lib/actionServerContext';
import { useLocalStorage } from '~/lib/useLocalStorage';
import {
  formDataToPayload,
  Payload,
  payloadToFormData,
  propertiesToFormData,
  PropertyFormData,
  PropertyFormDataType,
  setArrayItemTitle,
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

const asFloat = (v: string) => {
  // note: the current approach of always converting to the actual
  // data has a big drawback: the user can't have invalid data
  // temporarily (so, he can't enter 10e-10 as the 'e' can never
  // be entered and even if the user copies/pastes it the value
  // will be converted from the internal float value -- maybe
  // this should be revisited later on so that internal values
  // for basic types are always strings).
  // For the time being this is a limitation of the current approach
  // (so, it's possible that a Nan is generated here and then
  // the handleInputChange needs to guard against it).
  return parseFloat(v);
};

const asInt = (v: string) => {
  return parseInt(v, 10);
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
    if (typeof value === 'number') {
      if (Number.isNaN(value)) {
        // i.e.: this means the user entered a bad value. Don't enter it as the roundtrip
        // would make the user loose the current value up to this point.
        return;
      }
    }
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

        const ret = {
          ...item,
          name: newName,
        };
        setArrayItemTitle(item);
        return ret;
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
      let args;
      try {
        args = useRawJSON ? JSON.parse(formRawJSON) : formDataToPayload(formData);
      } catch (err) {
        // TODO: Use some better component from the design system.
        // eslint-disable-next-line no-alert
        alert(
          'Unable to run action because the input is not valid (the input cannot be converted to JSON).',
        );
        return;
      }
      runAction({
        actionPackageName: toKebabCase(actionPackage.name),
        actionName: toKebabCase(action.name),
        args,
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
        logError(err);
      }
    } else {
      try {
        if (formData.length === 0) {
          setFormRawJSON('');
        } else {
          const payload = formDataToPayload(formData);
          setFormRawJSON(JSON.stringify(payload, null, 4));
        }
      } catch (err) {
        logError(err);
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
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Input
                      key={`${title}-${item.name}-${index}`}
                      label={title}
                      description={item.property.description}
                      required={item.required}
                      value={typeof item.value === 'number' ? item.value.toString() : '0'}
                      type="number"
                      onChange={(e) => handleInputChange(asFloat(e.target.value), index)}
                    />
                  </Item>
                );
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
                      onChange={(e) => handleInputChange(asInt(e.target.value), index)}
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
                      value={
                        typeof item.value === 'string'
                          ? item.value.toString()
                          : JSON.stringify(item.value)
                      }
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
                  <ItemArray title={title} name={item.name} key={item.name}>
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
                      key={`${title}-${item.name}-${index}`}
                      label={title}
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
