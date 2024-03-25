/* eslint-disable camelcase */
import type { OpenAPIV3_1 } from 'openapi-types';
import { InputProperty } from './types';

export type PropertyFormDataType = string | number | boolean | Array<PropertyFormData>;

export type PropertyFormData = {
  name: string;
  property: InputProperty;
  required: boolean;
  value: PropertyFormDataType;
  title?: string;
  options?: string[];
};

const getDefaultValue = (property: OpenAPIV3_1.SchemaObject): PropertyFormDataType => {
  if (property.default) {
    return property.default;
  }

  switch (property.type) {
    case 'number':
      return 0.0;
    case 'boolean':
      return false;
    case 'integer':
      return 0;
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
      const rowEntry: PropertyFormData = {
        name: propertyName.join('.'),
        title: property.title || propertyName[propertyName.length - 1],
        property: {
          title: property.title || propertyName[propertyName.length - 1],
          description: property.description || '',
          type: 'array',
        },
        required: schema.required?.includes(name) || false,
        value: getDefaultValue(property),
      };

      if ('items' in property && property.items) {
        if ('properties' in property.items) {
          const rowProperties = propertiesToFormData(property.items, propertyName.concat(['0']));
          rowEntry.value = rowProperties;
          return [rowEntry].concat(rowProperties);
        }

        const rowProperty: PropertyFormData = {
          name: `${propertyName.join('.')}.0`,
          property: {
            title: property.title || propertyName[propertyName.length - 1],
            description: property.description || '',
            type:
              'type' in property.items && property.items.type && !Array.isArray(property.items.type)
                ? property.items.type
                : 'string',
          },
          required: schema.required?.includes(name) || false,
          value: getDefaultValue(property),
        };
        rowEntry.value = [rowProperty];

        return [rowEntry, rowProperty];
      }

      return [rowEntry];
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

export const formDatatoPayload = (data: PropertyFormData[]): Payload => {
  const result: Payload = {};

  data.forEach(({ name, value, property }) => {
    const levels = name.split('.');
    const propertyName = levels[levels.length - 1];

    let currentLevel = result;

    for (let i = 0; i < levels.length - 1; i += 1) {
      const level = levels[i];

      if (!currentLevel[level]) {
        currentLevel[level] = {};
      }

      currentLevel = currentLevel[level];
    }

    if (property.type === 'array') {
      if (!currentLevel[propertyName]) {
        currentLevel[propertyName] = [];
      }
    } else if (Array.isArray(currentLevel)) {
      currentLevel.push(value);
    } else {
      currentLevel[propertyName] = value;
    }
  });

  return result;
};
