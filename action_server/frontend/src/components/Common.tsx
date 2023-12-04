import { Content } from '@robocorp/components';
import { FC, ReactNode } from 'react';
import { Box } from '@robocorp/components';
import styled from 'styled-components';

export const PreBox = styled(Box)`
  white-space: pre-wrap;
  word-break: break-word;
  display: inline;
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

export const VariableHeader = styled(Box)`
  margin-top: ${({ theme }) => theme.space.$8};
  width: 100%;
  position: relative;
  display: flex;
  -webkit-box-align: center;
  align-items: center;
  border-bottom: 1px solid rgba(var(--color-border-primary));
  margin-top: ${({ theme }) => theme.space.$8};
`;

export const VariableHeaderBig = styled(Box)`
  margin-top: ${({ theme }) => theme.space.$8};
  width: 100%;
  font-
  position: relative;
  display: flex;
  -webkit-box-align: center;
  align-items: center;
  border-bottom: 1px solid rgba(var(--color-border-accent));
  margin-top: ${({ theme }) => theme.space.$8};
  font-size: larger;
`;

export const VariableContent = styled(Box)`
  margin-top: ${({ theme }) => theme.space.$8};
`;

export const MarginBotton = styled(Box)`
  margin-bottom: ${({ theme }) => theme.space.$40};
`;

export const VariableHeaderContent = styled(Box)`
  color: rgba(var(--color-content-accent));
  font-weight: 600;
  padding: 0.5rem 0px 1rem;
  border-bottom: 1px solid rgba(var(--color-border-accent));
`;

export const Variable: FC<{ name: string; value: ReactNode }> = ({ name, value }) => {
  return (
    <Content>
      <VariableHeader>
        <VariableHeaderContent>{name}</VariableHeaderContent>
      </VariableHeader>
      <VariableContent>
        <PreBox>{value}</PreBox>
      </VariableContent>
    </Content>
  );
};