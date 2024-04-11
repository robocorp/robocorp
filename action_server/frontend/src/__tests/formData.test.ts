/* eslint-disable @typescript-eslint/no-explicit-any */
import { expect, test } from 'vitest';
import { propertiesToFormData, formDataToPayload } from '../lib/formData';

import inputSchema from './fixtures/inputSchema.json';
import formData from './fixtures/formData.json';
import actionPayload from './fixtures/actionPayload.json';

test('Properties to Form Data', () => {
  expect(propertiesToFormData(inputSchema as any)).toStrictEqual(formData);
});

test('Form Data to Payload', () => {
  expect(formDataToPayload(formData as any)).toStrictEqual(actionPayload);
});
