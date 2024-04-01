import { FC, FormEvent, ReactNode, useCallback, useEffect, useMemo, useState } from 'react';
import {
  Box,
  Button,
  Checkbox,
  Form,
  Input,
  Select,
  Switch,
  Typography,
} from '@robocorp/components';

import { Action, ActionPackage } from '~/lib/types';
import { debounce, toKebabCase } from '~/lib/helpers';
import { useActionServerContext } from '~/lib/actionServerContext';
import { useLocalStorage } from '~/lib/useLocalStorage';
import { formDatatoPayload, propertiesToFormData, PropertyFormData } from '~/lib/formData';
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
    <Box pl={indent * 16}>
      {title && (
        <Typography mb="$8" variant="display.small">
          {title}
        </Typography>
      )}
      {children}
    </Box>
  );
};

export const ActionRun: FC<Props> = ({ action, actionPackage }) => {
  const [apiKey, setApiKey] = useLocalStorage<string>('api-key', '');
  const { serverConfig } = useActionServerContext();
  const [formData, setFormData] = useState<PropertyFormData[]>([]);
  const { mutate: runAction, isPending, isSuccess, data, reset } = useActionRunMutation();

  const [useRawJSON, setUseRawJSON] = useState<boolean>(false);
  const [errorJSON, setErrorJSON] = useState<string>();

  useEffect(() => {
    setFormData(propertiesToFormData(JSON.parse(action.input_schema)));
  }, [action, actionPackage]);

  const handleInputChange = useCallback(
    (value: string, index: number) => {
      setFormData((curr) => curr.map((item, idx) => (idx === index ? { ...item, value } : item)));
      reset();
    },
    [action, actionPackage, formData],
  );

  const onSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();

      runAction({
        actionPackageName: toKebabCase(actionPackage.name),
        actionName: toKebabCase(action.name),
        args: formDatatoPayload(formData),
        apiKey: serverConfig?.auth_enabled ? apiKey : undefined,
      });
    },
    [action, actionPackage, formData, apiKey, serverConfig],
  );

  const onCodeChange = useCallback(
    (code: string) => {
      try {
        setErrorJSON(undefined);
        const rawInputData = JSON.parse(code as string);
        const tempForm = [...formData];

        Object.entries(rawInputData).forEach(([key, val]) => {
          const foundFormItem = tempForm.find(
            (elem) => elem.name.toLowerCase() === key.toLowerCase(),
          );
          if (foundFormItem) {
            const foundFormItemIndex = tempForm.findIndex(
              (elem) => elem.name.toLowerCase() === key.toLowerCase(),
            );
            tempForm[foundFormItemIndex] = { ...foundFormItem, value: val as string };
          }
        });

        debounce(() => setFormData([...tempForm]), 750)();
      } catch (e) {
        console.error(`Error while generating entries: ${JSON.stringify(e)}`);
        setErrorJSON('Validating JSON syntax failed. Please verify the input and try again.');
      }
    },
    [formData],
  );

  const rawJSONInput = useMemo(() => {
    try {
      if (formData.length === 0) {
        return 'No input data...';
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const output: { [key: string]: any } = {};
      formData.forEach((prop) => {
        switch (prop.property.type) {
          case 'boolean':
            output[prop.name.toLowerCase()] = prop.value.toLowerCase() === 'true';
            break;
          case 'number':
          case 'integer':
            output[prop.name.toLowerCase()] = parseFloat(prop.value);
            break;
          case 'object':
            output[prop.name.toLowerCase()] = JSON.parse(prop.value);
            break;
          case 'enum':
          default:
            output[prop.name.toLowerCase()] = prop.value;
            break;
        }
      });
      return JSON.stringify(output, null, 4);
    } catch (e) {
      console.error(`Error collecting raw JSON input: ${JSON.stringify(e)}`);
      return 'There was an error while parsing form data...';
    }
  }, [formData]);

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
      <Form.Fieldset>
        {useRawJSON ? (
          <Code
            lang="json"
            aria-label="Run JSON input"
            value={rawJSONInput}
            onChange={onCodeChange}
            error={errorJSON}
            readOnly={false}
          />
        ) : (
          formData.map((item, index) => {
            const title = `${item.property.title}${item.required ? ' *' : ''}`;

            switch (item.property.type) {
              case 'boolean':
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Checkbox
                      key={item.name}
                      label={title}
                      description={item.property.description}
                      checked={item.value === 'True'}
                      required={item.required}
                      onChange={(e) =>
                        handleInputChange(e.target.checked ? 'True' : 'False', index)
                      }
                    />
                  </Item>
                );
              case 'number':
              case 'integer':
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Input
                      key={item.name}
                      label={title}
                      description={item.property.description}
                      required={item.required}
                      value={item.value}
                      type="number"
                      onChange={(e) => handleInputChange(e.target.value, index)}
                    />
                  </Item>
                );
              case 'object':
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Input
                      key={item.name}
                      label={title}
                      description={item.property.description}
                      required={item.required}
                      value={item.value}
                      rows={4}
                      onChange={(e) => handleInputChange(e.target.value, index)}
                    />
                  </Item>
                );
              case 'enum':
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Select
                      key={item.name}
                      label={title}
                      description={item.property.description}
                      required={item.required}
                      value={item.value}
                      items={item.options?.map((value) => ({ label: value, value })) || []}
                      onChange={(e) => handleInputChange(e, index)}
                    />
                  </Item>
                );
              case 'string':
              default:
                return (
                  <Item title={item.title} name={item.name} key={item.name}>
                    <Input
                      key={item.name}
                      label={title}
                      description={item.property.description}
                      rows={1}
                      required={item.required}
                      value={item.value}
                      onChange={(e) => handleInputChange(e.target.value, index)}
                    />
                  </Item>
                );
            }
          })
        )}
      </Form.Fieldset>
      <Button.Group align="right" justifyContent="space-between" alignItems="center" pb={16}>
        <Button loading={isPending} type="submit" variant="primary">
          Run
        </Button>
        <Switch
          label=""
          value="Use JSON"
          checked={useRawJSON}
          onChange={(e) => setUseRawJSON(e.target.checked)}
        />
      </Button.Group>
      {isSuccess && <ActionRunResult result={data.response} runId={data.runId} />}
    </Form>
  );
};
