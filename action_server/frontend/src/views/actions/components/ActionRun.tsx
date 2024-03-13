import { ChangeEvent, FC, FormEvent, useCallback, useEffect, useState } from 'react';
import { Button, Checkbox, Form, Header, Input, Typography } from '@robocorp/components';

import { runAction } from '~/lib/requestData';
import { Action, ActionPackage, AsyncLoaded, InputPropertyType } from '~/lib/types';
import { Code } from '~/components';
import { toKebabCase, stringifyResult } from '~/lib/helpers';
import { useActionServerContext } from '~/lib/actionServerContext';
import { useLocalStorage } from '~/lib/useLocalStorage';
import { formDatatoPayload, propertiesToFormData, PropertyFormData } from '~/lib/formData';

type Props = {
  action: Action;
  actionPackage: ActionPackage;
};

type RunResult = string | number | boolean | undefined;

const dataLoadedInitial: AsyncLoaded<RunResult> = {
  data: undefined,
  isPending: false,
};

export const ActionRun: FC<Props> = ({ action, actionPackage }) => {
  const [apiKey, setApiKey] = useLocalStorage<string>('api-key', '');
  const { serverConfig } = useActionServerContext();
  const [formData, setFormData] = useState<PropertyFormData[]>([]);
  const [result, setResult] = useState<AsyncLoaded<RunResult>>(dataLoadedInitial);

  useEffect(() => {
    setFormData(propertiesToFormData(JSON.parse(action.input_schema)));
  }, [action, actionPackage]);

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>, index: number) => {
      setFormData((curr) => {
        return curr.map((item, idx) => {
          if (idx !== index) {
            return item;
          }

          const updatedItem = { ...item };

          if (item.property.type === InputPropertyType.BOOLEAN) {
            updatedItem.value = e.target.checked ? 'True' : 'False';
          } else {
            updatedItem.value = e.target.value;
          }

          return updatedItem;
        });
      });

      setResult(dataLoadedInitial);
    },
    [action, actionPackage, dataLoadedInitial, formData],
  );

  const onSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      if (action?.name && actionPackage?.name) {
        runAction(
          toKebabCase(actionPackage.name),
          toKebabCase(action.name),
          formDatatoPayload(formData),
          setResult,
          serverConfig?.auth_enabled ? apiKey : undefined,
        );
      }
    },
    [action, actionPackage, formData],
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
      <Form.Fieldset>
        {formData.map((item, index) => {
          const title = `${item.property.title}${item.required ? ' *' : ''}`;

          switch (item.property.type) {
            case InputPropertyType.BOOLEAN:
              return (
                <>
                  {item.title && <Typography variant="display.small">{item.title}</Typography>}
                  <Checkbox
                    key={item.name}
                    label={title}
                    description={item.property.description}
                    checked={item.value === 'True'}
                    required={item.required}
                    onChange={(e) => handleInputChange(e, index)}
                  />
                </>
              );
            case InputPropertyType.FLOAT:
            case InputPropertyType.NUMBER:
            case InputPropertyType.INTEGER:
              return (
                <>
                  {item.title && <Typography variant="display.small">{item.title}</Typography>}
                  <Input
                    key={item.name}
                    label={title}
                    description={item.property.description}
                    required={item.required}
                    value={item.value}
                    type="number"
                    onChange={(e) => handleInputChange(e, index)}
                  />
                </>
              );
            case InputPropertyType.OBJECT:
              return (
                <>
                  {item.title && <Typography variant="display.small">{item.title}</Typography>}
                  <Input
                    key={item.name}
                    label={title}
                    description={item.property.description}
                    required={item.required}
                    value={item.value}
                    rows={4}
                    onChange={(e) => handleInputChange(e, index)}
                  />
                </>
              );
            case InputPropertyType.STRING:
            default:
              return (
                <>
                  {item.title && <Typography variant="display.small">{item.title}</Typography>}
                  <Input
                    key={item.name}
                    label={title}
                    description={item.property.description}
                    rows={1}
                    required={item.required}
                    value={item.value}
                    onChange={(e) => handleInputChange(e, index)}
                  />
                </>
              );
          }
        })}
      </Form.Fieldset>
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
