import { ComponentProps, FC, useEffect, useMemo, useRef } from 'react';
import { Code as BaseCode, Box, EditorView } from '@robocorp/components';
import { StreamLanguage } from '@codemirror/language';
import { shell } from '@codemirror/legacy-modes/mode/shell';
import { json } from '@codemirror/lang-json';

import { CopyToClipboard } from '~/components';

export const SUPPORTED_CODE_MODES = ['sh', 'json'] as const;

export interface CodeProps
  extends Omit<ComponentProps<typeof BaseCode>, 'extensions' | 'codemirrorRef'> {
  mode?: (typeof SUPPORTED_CODE_MODES)[number];
  autoFocus?: boolean;
  lineWrapping?: boolean;
  height?: number;
  copyValue?: string;
}

export const Code: FC<CodeProps> = ({
  mode = 'json',
  lineWrapping = false,
  autoFocus,
  height,
  value,
  copyValue,
  ...restProps
}) => {
  const codemirror = useRef<EditorView>();

  const toolbar = useMemo(() => {
    return <CopyToClipboard variant="ghost" round value={copyValue || value} />;
  }, [copyValue, value]);

  const extensions = useMemo(() => {
    const extensionList = [];

    if (lineWrapping) {
      extensionList.push(EditorView.lineWrapping);
    }

    switch (mode) {
      case 'json':
        extensionList.push(json());
        break;
      case 'sh':
        extensionList.push(StreamLanguage.define(shell));
        break;
      default:
        break;
    }

    return extensionList;
  }, [mode, lineWrapping]);

  useEffect(() => {
    if (autoFocus) {
      codemirror.current?.focus();
    }
  }, [autoFocus]);

  return (
    <Box height={height} mb="$24">
      <BaseCode
        extensions={extensions}
        codemirrorRef={codemirror}
        aria-labelledby="code"
        theme="dark"
        value={value}
        toolbar={toolbar}
        readOnly
        lineNumbers={false}
        {...restProps}
      />
    </Box>
  );
};
