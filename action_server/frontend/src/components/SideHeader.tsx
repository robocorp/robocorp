import { FC, useCallback } from 'react';
import { Box, Typography, usePopover } from '@robocorp/components';
import { IconGlobe, IconLink } from '@robocorp/icons/iconic';
import { styled } from '@robocorp/theme';

import { useActionServerContext } from '~/lib/actionServerContext';
import { ActionServerLogo } from './Logo';
import { InputCopy } from './CopyToClipboard';

const Container = styled(Box)`
  cursor: pointer;
`;

const ExposedIcon = styled(Box)<{ $enabled: boolean }>`
  position: relative;
  width: ${({ theme }) => theme.sizes.$24};
  height: ${({ theme }) => theme.sizes.$24};

  &::after {
    display: ${({ $enabled }) => ($enabled ? 'none' : 'block')};
    position: absolute;
    content: '';
    left: 50%;
    top: 0;
    width: 2px;
    height: 100%;
    background: currentColor;
    border-radius: 2px;
    transform: rotate(-45deg);
  }

  > svg {
    display: block;
  }
`;

export const SideHeader: FC = () => {
  const { serverConfig } = useActionServerContext();

  const { referenceRef, referenceProps, PopoverContent, setOpen } = usePopover({
    placement: 'right',
    width: 440,
    offset: 0,
  });

  const onMouseOver = useCallback(() => {
    setOpen(true);
  }, []);

  const onMouseLeave = useCallback(() => {
    setOpen(false);
  }, []);

  const isExposed = !!serverConfig?.expose_url;

  return (
    <Box onMouseLeave={onMouseLeave}>
      <Container
        ref={referenceRef}
        {...referenceProps}
        display="flex"
        alignItems="center"
        gap="$8"
        height="$32"
        mb="$48"
        px="$8"
        onMouseOver={onMouseOver}
      >
        <Box
          display="flex"
          borderRadius="$8"
          width="$32"
          height="$32"
          backgroundColor="blue70"
          alignItems="center"
          justifyContent="center"
        >
          <ActionServerLogo size={20} />
        </Box>
        <Typography fontWeight={600}>Action Server</Typography>
        <ExposedIcon $enabled={isExposed} ml="auto">
          <IconGlobe size={24} />
        </ExposedIcon>
      </Container>
      <PopoverContent>
        <Box p="$16" backgroundColor="background.primary" borderRadius="$8" boxShadow="medium">
          {isExposed ? (
            <>
              <Typography fontWeight="bold" mb="$16">
                Action Server exposed
              </Typography>
              <Box mb="$16">
                <InputCopy
                  iconLeft={IconLink}
                  label="Server URL"
                  value={serverConfig.expose_url}
                  readOnly
                />
              </Box>
            </>
          ) : (
            <>
              <Typography fontWeight="bold" mb="$16">
                Action Server not exposed
              </Typography>
              <Typography lineHeight="$16" mb="$12">
                To serve a public URL for your ACtion Server, start it with the{' '}
                <Typography as="span" color="content.accent">
                  --expose
                </Typography>{' '}
                parameter set.
              </Typography>
              <InputCopy
                aria-label="Expose command"
                value="action-server start --expose"
                readOnly
              />
            </>
          )}
        </Box>
      </PopoverContent>
    </Box>
  );
};
