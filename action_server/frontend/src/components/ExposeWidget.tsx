import { FC } from 'react';
import { Box, Header, Typography } from '@robocorp/components';

import { Code } from '~/components';

const getStarted = `#!/bin/bash

# Create a boileplate action project
action-server new  `;

export const ExposeWidget: FC = () => {
  return (
    <>
      <Header>
        <Header.Title title="Server Expose" />
      </Header>
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
        <Code value={getStarted} copyValue="action-server new" mode="sh" />
      </Box>
    </>
  );
};
