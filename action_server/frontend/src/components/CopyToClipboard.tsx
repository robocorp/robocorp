import { FC, useState, useEffect } from 'react';
import { Button, ButtonProps, Tooltip } from '@robocorp/components';
import { IconCheck2, IconCopy } from '@robocorp/icons/iconic';

type Props = {
  value: string;
} & Pick<ButtonProps, 'disabled' | 'variant' | 'round' | 'flex'>;

const CopyToClipboard: FC<Props> = ({ value, ...rest }) => {
  const [clicked, setClicked] = useState(false);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setClicked(false);
    }, 2000);

    return () => {
      clearTimeout(timeout);
    };
  }, [clicked, setClicked]);

  const copyToClipboard = () => {
    const dummy = document.createElement('textarea');
    document.body.appendChild(dummy);
    dummy.innerHTML = value;
    dummy.select();
    dummy.focus();
    document.execCommand('copy');
    document.body.removeChild(dummy);
    setClicked(true);
  };

  return (
    <Tooltip text="Copy to Clipboard" placement="top">
      <Button
        icon={clicked ? IconCheck2 : IconCopy}
        onClick={copyToClipboard}
        aria-label="copy to clipboard"
        {...rest}
      />
    </Tooltip>
  );
};

export default CopyToClipboard;
