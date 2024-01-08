import { Dispatch, SetStateAction, useEffect, useState } from 'react';

const getFromLocalStorage = <T>(key: string, fallback: T, merge: boolean): T => {
  const localValue = window?.localStorage.getItem(key);

  try {
    if (localValue) {
      const parsed = JSON.parse(localValue) as T;
      return merge ? { ...fallback, ...parsed } : parsed;
    }
  } catch (_err) {
    return fallback;
  }

  return fallback;
};

export const useLocalStorage = <T>(
  key: string,
  initialValue: T,
  merge = false,
): [T, Dispatch<SetStateAction<T>>] => {
  const [payload, setPayload] = useState<T>(getFromLocalStorage(key, initialValue, merge));

  useEffect(() => {
    window?.localStorage.setItem(key, JSON.stringify(payload));
  }, [payload]);

  return [payload, setPayload];
};
