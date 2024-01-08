import { ComponentProps } from 'react';
import { componentWithRef, Grid } from '@robocorp/components';
import { styled } from '@robocorp/theme';
import { DefinitionListKey, DefinitionListValue } from './components/Item';

const compoundComponents = {
  Key: DefinitionListKey,
  Value: DefinitionListValue,
};

const Container = styled(Grid)`
  grid-template-columns: 25% 65%;
  background-color: ${({ theme }) => theme.color('background.subtle')};
  border-radius: ${({ theme }) => theme.radii.$16};
  margin-bottom: ${({ theme }) => theme.space.$24};
`;

/**
 * Component to display a key value information in list like fashion
 *
 * @example
 * <DefinitionList>
 *   <DefinitionList.Key>foo<DefinitionList.Key>
 *   <DefinitionList.Value>bar<DefinitionList.Value>
 * </FileList>
 */
export const DefinitionList = componentWithRef<
  ComponentProps<typeof Grid>,
  HTMLDivElement,
  typeof compoundComponents
>(
  (props, forwardedRef) => <Container columns={2} gap={0} py="$16" ref={forwardedRef} {...props} />,
  compoundComponents,
);
