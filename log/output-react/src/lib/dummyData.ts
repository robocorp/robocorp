import { Entry, Status, Type } from './types';

export const dummyData = (): Entry[] => {
  return Array.from(Array(1000).keys()).flatMap((_item, index) => [
    {
      id: `${index}`,
      type: Type.suite,
      source: 'challenge.py',
      duration: 100,
      lineNo: 1,
      date: new Date(),
      name: 'fill_and_submit_the_form',
    },
    {
      id: `${index}-1`,
      type: Type.suite,
      source: 'challenge-long-name.py',
      duration: 100,
      lineNo: 1,
      date: new Date(),
      name: 'run',
    },
    {
      id: `${index}-1-1`,
      type: Type.log,
      source: 'challenge.py',
      duration: 100,
      lineNo: 3,
      date: new Date(),
      status: Status.info,
      message: 'Log: Run Started from 128.173.129.236',
    },
    {
      id: `${index}-1-2`,
      type: Type.variable,
      source: 'challenge.py',
      duration: 100,
      lineNo: 3,
      date: new Date(),
      name: 'initial0',
      value: 'Foo Bar Baz Foo Bar Baz Foo Bar Baz Foo Bar Baz Foo Bar Baz Foo Bar Baz',
    },
    {
      id: `${index}-1-2`,
      type: Type.error,
      source: 'challenge.py',
      duration: 100,
      lineNo: 3,
      date: new Date(),
      message: 'Some error \nWith multiple lines \nOf error value\nFoo Bar baz',
    },
  ]);
};
