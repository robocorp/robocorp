import { FC, useState, useEffect } from 'react';
import {
  Button,
  ButtonProps,
  Input,
  InputProps,
  Tooltip,
  useClipboard,
} from '@robocorp/components';
import { IconCheck2, IconCopy } from '@robocorp/icons/iconic';

type Props = {
  value: string;
} & Pick<ButtonProps, 'disabled' | 'variant' | 'round' | 'flex'>;

export const CopyToClipboard: FC<Props> = ({ value, ...rest }) => {
  const [clicked, setClicked] = useState(false);
  const { onCopyToClipboard, copiedToClipboard } = useClipboard();

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setClicked(false);
    }, 2000);

    return () => {
      clearTimeout(timeout);
    };
  }, [clicked, setClicked]);

  return (
    <Tooltip text="Copy to Clipboard" placement="top">
      <Button
        icon={copiedToClipboard ? IconCheck2 : IconCopy}
        onClick={onCopyToClipboard(value)}
        aria-label="copy to clipboard"
        size="small"
        {...rest}
      />
    </Tooltip>
  );
};

export const InputCopy: FC<InputProps & { value: string }> = ({ value, ...rest }) => {
  const { onCopyToClipboard, copiedToClipboard } = useClipboard();

  return (
    <Input
      value={value}
      onIconRightClick={onCopyToClipboard(value)}
      iconRight={copiedToClipboard ? IconCheck2 : IconCopy}
      iconRightLabel="Copy value"
      {...rest}
    />
  );
};
