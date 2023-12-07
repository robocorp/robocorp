import { ChangeEvent, FC, FormEvent, ReactNode, useCallback, useMemo, useState } from 'react';
import { Counter } from '~/lib/helpers';
import { prettyPrint } from '~/lib/prettyPrint';
import { Action, ActionPackage, AsyncLoaded } from '~/lib/types';
import { MarginBotton, Variable, VariableHeaderBig, VariableHeaderContent } from './Common';
import { useActionsContext } from './ActionPackages';
import { Box, Drawer, Form, Input, Button } from '@robocorp/components';
import { runAction } from '~/lib/requestData';

interface Value {
  type: string;
  description: string;
  title: string;
}

const dataLoadedInitial: AsyncLoaded<any> = {
  data: undefined,
  isPending: false,
};

const nameToUrl = (name: string): string => {
  return name.replace('_', '-');
};

const convertType = (v: string, valueType: string): string | number | boolean => {
  switch (valueType) {
    case 'string':
      return v;
    case 'number':
      return parseFloat(v);
    case 'integer':
      return parseInt(v);
    case 'boolean':
      if (v === 'false') {
        return false;
      }
      if (v === 'true') {
        return true;
      }
      throw new Error(`Unable to convert: ${v} to a boolean.`);
  }
  return '';
};

export const ActionRunControls: FC<{
  action: Action | undefined;
  actionPackage: ActionPackage | undefined;
}> = ({ action, actionPackage }) => {
  const inputSchema: any = useMemo(() => {
    if (action === undefined) {
      return {};
    }
    return JSON.parse(action.input_schema);
  }, [action, actionPackage]);

  const properties: [string, Value][] = useMemo(() => {
    const found = inputSchema['properties'];
    if (found === undefined) {
      return [];
    }
    return Object.entries(found) as unknown as [string, Value][];
  }, [action, actionPackage]);

  const initialFormData = useMemo(() => {
    const initialFormData: any = {};
    if (action?.input_schema) {
      const required = inputSchema.required;
      for (const [key, value] of properties) {
        const isRequired = required.includes(key);
        const valueType = value['type'];
        if (isRequired) {
          if (valueType === 'string') {
            initialFormData[key] = '';
          } else if (valueType === 'number') {
            initialFormData[key] = '0.0';
          } else if (valueType === 'boolean') {
            initialFormData[key] = 'true';
          } else if (valueType === 'integer') {
            initialFormData[key] = '0';
          }
        }
      }
    }
    return initialFormData;
  }, [action, actionPackage, properties]);

  const [formData, setFormData] = useState(initialFormData);
  const [result, setResult] = useState<AsyncLoaded<any>>(dataLoadedInitial);

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>, propertyName: string) => {
      const value = e.target.value;
      setFormData((formData: any) => {
        return {
          ...formData,
          [propertyName]: value,
        };
      });
      setResult(dataLoadedInitial);
    },
    [action, actionPackage, dataLoadedInitial, formData],
  );

  const fields: ReactNode[] = useMemo(() => {
    const fields: ReactNode[] = [];
    if (properties.length > 0) {
      const required = inputSchema.required;

      for (const [key, value] of properties) {
        const isRequired = required.includes(key);
        const valueType = value['type'];
        const description = value['description'];
        let title = `${value['title']} (${valueType})`;
        if (isRequired) {
          title += ' *';
        }

        if (valueType === 'string') {
          fields.push(
            <Input
              key={key}
              label={title}
              rows={5}
              placeholder={undefined}
              description={description}
              value={formData[key]}
              onChange={(e) => handleInputChange(e, key)}
            />,
          );
        } else {
          fields.push(
            <Input
              key={key}
              label={title}
              placeholder={undefined}
              description={description}
              value={formData[key]}
              onChange={(e) => handleInputChange(e, key)}
            />,
          );
        }
      }
    }
    return fields;
  }, [action, actionPackage, inputSchema, handleInputChange, properties]);

  const onSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      const useData: any = {};
      for (const [key, val] of Object.entries(formData)) {
        const valueType = inputSchema['properties'][key]['type'];
        useData[key] = convertType(val as string, valueType);
      }
      if (action?.name && actionPackage?.name) {
        runAction(nameToUrl(actionPackage.name), nameToUrl(action.name), useData, setResult);
      }
    },
    [formData, action, actionPackage, inputSchema, result, setResult],
  );

  let resultComponent = <></>;
  if (!result.isPending && (result.data !== undefined || result.errorMessage)) {
    if (result.errorMessage) {
      resultComponent = <Variable name={'Result'} value={'' + result.errorMessage}></Variable>;
    } else {
      resultComponent = <Variable name={'Result'} value={'' + result.data}></Variable>;
    }
  }
  return (
    <>
      <VariableHeaderBig>
        <VariableHeaderContent>{'Run'}</VariableHeaderContent>
      </VariableHeaderBig>
      <Box>
        <Form busy={result.isPending} onSubmit={onSubmit}>
          <Form.Fieldset>{fields}</Form.Fieldset>
          {resultComponent}
          <Button.Group align="right">
            <Button loading={result.isPending} type="submit" variant="primary">
              Run
            </Button>
          </Button.Group>
        </Form>
      </Box>
    </>
  );
};

export const ActionRawDetails: FC<{ action: Action | undefined }> = ({ action }) => {
  const counter = new Counter();
  const contents = [];

  let inputSchema = action?.input_schema;
  if (!inputSchema) {
    inputSchema = '<unable to get input schema>';
  }

  let outputSchema = action?.output_schema;
  if (!outputSchema) {
    outputSchema = '<unable to get output schema>';
  }

  let docs = action?.docs;
  if (docs === undefined) {
    docs = '';
  }

  contents.push(<Variable key={counter.next()} name={`Documentation`} value={docs} />);

  contents.push(
    <Variable key={counter.next()} name={`Input Schema`} value={prettyPrint(inputSchema)} />,
  );

  contents.push(
    <Variable key={counter.next()} name={`Output Schema`} value={prettyPrint(outputSchema)} />,
  );

  return <>{contents}</>;
};

export const ActionDetails: FC<{}> = ({}) => {
  const { showAction, setShowAction } = useActionsContext();
  const onClose = useCallback(() => {
    setShowAction(undefined);
  }, []);

  if (showAction === undefined) {
    return <></>;
  }

  return (
    <Drawer passive onClose={onClose} width={1024} open={true}>
      <Drawer.Header>
        <Drawer.Header.Title title={showAction.action.name} />
      </Drawer.Header>
      <Drawer.Content>
        <ActionRunControls action={showAction.action} actionPackage={showAction.actionPackage} />
        <ActionRawDetails action={showAction.action} />
        <MarginBotton />
      </Drawer.Content>
    </Drawer>
  );
};
