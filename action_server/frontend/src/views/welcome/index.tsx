import { FC, useCallback } from 'react';
import { Box, Grid, Typography, useTheme } from '@robocorp/components';
import { Color, styled } from '@robocorp/theme';

import { Code } from '~/components';
import { OnboardingCard } from './components/Card';
import { IconPython } from './components/Icons';

const Container = styled.div`
  .cm-editor {
    .ͼ14 {
      color: ${({ theme }) => theme.colors.content.disabled.color};
    }
  }
`;

const getStarted = `#!/bin/bash

# Create a boileplate action project
action-server new  `;

export const Welcome: FC = () => {
  const theme = useTheme();

  const purple: Color = theme.name === 'light' ? 'purple20' : 'purple80';
  const orange: Color = theme.name === 'light' ? 'orange20' : 'orange80';

  const onOpenTutorial = useCallback(
    (url: string) => () => {
      window.open(url, '_');
    },
    [],
  );

  return (
    <Container>
      <Box display="flex" flexDirection="column" maxWidth={720} margin="0 auto" my={20}>
        <Box display="flex" flexDirection="column">
          <Box display="flex" justifyContent="center">
            <span role="img" aria-label="get-started">
              👋
            </span>
          </Box>
          <Typography fontSize="$28" textAlign="center" fontWeight={600} my="$24">
            Welcome to Action Server!
          </Typography>
        </Box>
        <Typography fontSize="$16" lineHeight={1.4} my="$16">
          Looks like you do not have any actions created yet. You can get started by creating a
          template using Avtion Server itself:
        </Typography>
        <Code value={getStarted} copyValue="action-server new" mode="sh" lineNumbers={false} />
        <Typography fontSize="$16" lineHeight={1.4} mt="$16">
          Or check out some of our examples:
        </Typography>
      </Box>
      <Box display="flex" flexDirection="column" maxWidth={720} margin="0 auto">
        <Box maxWidth={720}>
          <Grid columns={[1, 2, 3]} gap="$24">
            <OnboardingCard
              onClick={onOpenTutorial('https://robocorp.com/portal')}
              icon={<IconPython />}
              thumbnailColor={purple}
              title="Action example #1"
              description="A short action example on what it does and what libs it uses."
            />
            <OnboardingCard
              onClick={onOpenTutorial('https://robocorp.com/portal')}
              icon={<IconPython />}
              thumbnailColor={orange}
              title="Action example #2"
              description="A short action example on what it does and what libs it uses."
            />
            <OnboardingCard
              onClick={onOpenTutorial('https://robocorp.com/portal')}
              icon={<IconPython />}
              thumbnailColor="grey80"
              title="Action example #3"
              description="A short action example on what it does and what libs it uses."
            />
          </Grid>
        </Box>
      </Box>
    </Container>
  );
};
