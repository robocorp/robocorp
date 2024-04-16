/* eslint-disable @typescript-eslint/no-explicit-any */
import { expect, test } from 'vitest';
import {
  propertiesToFormData,
  formDataToPayload,
  payloadToFormData,
  PropertyFormData,
} from '../lib/formData';

import inputSchema from './fixtures/inputSchema.json';
import formData from './fixtures/formData.json';
import actionPayload from './fixtures/actionPayload.json';

import case2InputSchema from './fixtures/case2InputSchema.json';
import case2FormData from './fixtures/case2FormData.json';
import case2ActionPayload from './fixtures/case2ActionPayload.json';

test('Properties to Form Data', () => {
  expect(propertiesToFormData(inputSchema as any)).toStrictEqual(formData);
});

test('Form Data to Payload', () => {
  expect(formDataToPayload(formData as any)).toStrictEqual(actionPayload);
});

test('Properties to Form Data, Case 2', () => {
  const found = propertiesToFormData(case2InputSchema as any);
  expect(found).toStrictEqual(case2FormData);
});

test('Form Data to Payload, Case 2', () => {
  const found = formDataToPayload(case2FormData as any);
  expect(found).toStrictEqual(case2ActionPayload);
});

test('Payload to Form Data, Case 2', () => {
  const converted = payloadToFormData(
    { arg: 1, data: { rows: [3, 4], others: { A: [true] } } },
    <PropertyFormData[]>case2FormData,
  );

  expect(converted).toStrictEqual([
    {
      name: 'arg',
      property: { title: 'Arg', description: 'Some arg', type: 'integer' },
      required: true,
      value: 1,
    },
    {
      name: 'data.rows',
      title: 'Rows',
      property: { title: 'Rows', description: '', type: 'array' },
      required: true,
      value: [
        {
          name: 'data.rows.0',
          property: { title: 'Rows (item)', description: '', type: 'integer' },
          required: true,
          value: 0,
        },
      ],
    },
    {
      name: 'data.rows.0',
      property: { title: 'Rows (item)', description: '', type: 'integer' },
      required: true,
      value: 3,
    },
    {
      name: 'data.rows.1',
      property: { title: 'Rows (item)', description: '', type: 'integer' },
      required: true,
      value: 4,
    },
    {
      name: 'data.others',
      property: { title: 'Others', description: '', type: 'object' },
      required: true,
      value: { A: [true] },
    },
  ]);
});
