import { InputSchema, InputProperty, InputPropertyType } from './types';

export type PropertyFormData = {
  name: string;
  property: InputProperty;
  required: boolean;
  value: string;
  title?: string;
};

const getDefaultValue = (property: InputProperty): string => {
  if (property.default) {
    return typeof property.default === 'string'
      ? property.default
      : JSON.stringify(property.default);
  }

  switch (property.type) {
    case InputPropertyType.NUMBER:
      return '0.0';
    case InputPropertyType.BOOLEAN:
      return 'False';
    case InputPropertyType.INTEGER:
      return '0';
    case InputPropertyType.STRING:
    default:
      return '';
  }
};

export const propertiesToFormData = (
  schema: InputSchema,
  parents: string[] = [],
): PropertyFormData[] => {
  const entries = Object.entries(schema.properties).flatMap(([name, property], index) => {
    const propertyName = parents.concat([name]);

    if ('properties' in property) {
      return propertiesToFormData(property, propertyName);
    }

    const entry: PropertyFormData = {
      name: propertyName.join('.'),
      property: {
        title: property.title,
        description: property.description,
        type: property.type || 'string',
      },
      required: schema.required?.includes(name) || false,
      value: getDefaultValue(property),
    };

    if (index === 0) {
      entry.title = schema.title;
    }

    return [entry];
  });

  return entries;
};

type Payload = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
};

const convertValueToType = (
  value: string,
  valueType: InputPropertyType,
): string | number | boolean | object => {
  switch (valueType) {
    case InputPropertyType.NUMBER:
      return parseFloat(value);
    case InputPropertyType.INTEGER:
      return parseInt(value, 10);
    case InputPropertyType.BOOLEAN:
      if (value === 'False') {
        return false;
      }
      if (value === 'True') {
        return true;
      }
      throw new Error(`Unable to convert: ${value} to a boolean.`);
    case InputPropertyType.OBJECT:
      return JSON.parse(value);
    case InputPropertyType.STRING:
    default:
      return value;
  }
};

export const formDatatoPayload = (data: PropertyFormData[]): Payload => {
  const result: Payload = {};

  data.forEach(({ name, value, property }) => {
    const parts = name.split('.');
    let currentLevel = result;

    for (let i = 0; i < parts.length - 1; i += 1) {
      const part = parts[i];

      if (!currentLevel[part]) {
        currentLevel[part] = {};
      }

      currentLevel = currentLevel[part];
    }

    currentLevel[parts[parts.length - 1]] = convertValueToType(value, property.type);
  });

  return result;
};
