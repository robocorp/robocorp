import { FC, ReactNode } from 'react';
import { Box, Typography } from '@robocorp/components';

type Props = {
  children: ReactNode;
};

export const ViewError: FC<Props> = ({ children }) => {
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
      <Typography>{children}</Typography>
    </Box>
  );
};
