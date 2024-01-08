import { FC, useEffect, useState } from 'react';
import { Box, Progress } from '@robocorp/components';

type Props = {
  /**
   * Delay in seconds of the loader render
   */
  delay?: number;
};

/**
 * Full page loading placeholder for when no other content is available to display yet
 */
export const ViewLoader: FC<Props> = ({ delay }) => {
  const [ready, setReady] = useState<boolean>(false);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setReady(true);
    }, 800);

    return () => {
      clearTimeout(timeout);
    };
  }, [delay]);

  if (delay && !ready) {
    return null;
  }

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="100%"
      maxWidth={480}
      margin="0 auto"
      as="section"
    >
      <Progress variant="linear" />
    </Box>
  );
};
