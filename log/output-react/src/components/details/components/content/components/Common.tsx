import { Box } from '@robocorp/components';
import { styled } from '@robocorp/theme';

export const Bold = styled(Box)`
  font-weight: bold;
  display: inline;
`;

export const LocationContent = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$12};
  margin-bottom: ${({ theme }) => theme.space.$8};
`;
