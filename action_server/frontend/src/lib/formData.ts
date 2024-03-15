/* eslint-disable camelcase */
import type { OpenAPIV3_1 } from 'openapi-types';
import { InputProperty } from './types';

export type PropertyFormData = {
  name: string;
  property: InputProperty;
  required: boolean;
  value: string;
  title?: string;
  options?: string[];
};

const getDefaultValue = (property: OpenAPIV3_1.SchemaObject): string => {
  if (property.default) {
    return typeof property.default === 'string'
      ? property.default
      : JSON.stringify(property.default);
  }

  switch (property.type) {
    case 'number':
      return '0.0';
    case 'boolean':
      return 'False';
    case 'integer':
      return '0';
    case 'string':
    default:
      return '';
  }
};

export const propertiesToFormData = (
  schema: OpenAPIV3_1.BaseSchemaObject,
  parents: string[] = [],
): PropertyFormData[] => {
  if (!schema.properties) {
    return [];
  }

  const entries = Object.entries(schema.properties).flatMap(([name, property], index) => {
    const propertyName = parents.concat([name]);

    // Reference object should not be available they are dereferenced
    if ('$ref' in property) {
      return [];
    }

    // Nested properties
    if ('properties' in property) {
      return propertiesToFormData(property, propertyName);
    }

    if (property.allOf) {
      const firstChild = property.allOf[0];

      // enum
      if (firstChild && 'enum' in firstChild) {
        const entry: PropertyFormData = {
          name: propertyName.join('.'),
          property: {
            title: property.title || propertyName[propertyName.length - 1],
            description: property.description || '',
            type: 'enum',
          },
          required: schema.required?.includes(name) || false,
          value: property.default || firstChild.enum?.[0] || '',
          options: firstChild.enum,
        };

        return [entry];
      }

      return property.allOf.flatMap((item) => propertiesToFormData(item, propertyName)) || [];
    }

    if (Array.isArray(property.type) || property.type === 'array') {
      return [];
    }

    const entry: PropertyFormData = {
      name: propertyName.join('.'),
      property: {
        title: property.title || propertyName[propertyName.length - 1],
        description: property.description || '',
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
  valueType: OpenAPIV3_1.NonArraySchemaObjectType | 'enum',
): string | number | boolean | object => {
  switch (valueType) {
    case 'number':
      return parseFloat(value);
    case 'integer':
      return parseInt(value, 10);
    case 'boolean':
      if (value === 'False') {
        return false;
      }
      if (value === 'True') {
        return true;
      }
      throw new Error(`Unable to convert: ${value} to a boolean.`);
    case 'object':
      return JSON.parse(value);
    case 'string':
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
