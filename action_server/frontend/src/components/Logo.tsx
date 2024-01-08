import { forwardRef, useMemo } from 'react';
import { IconProps } from '@robocorp/icons';
import { styled } from '@robocorp/theme';

const IconStyled = styled.span`
  display: inline-block;
  svg {
    display: block;
  }
`;

/**
 * Action Server Logo icon
 * @example
 * <Logo size="large" />
 */
export const ActionServerLogo = forwardRef<HTMLSpanElement, IconProps>(
  ({ size: sizeProp, ...rest }, forwardedRef) => {
    const $size = useMemo(() => {
      switch (sizeProp) {
        case 'small':
          return '1rem';
        case 'large':
          return '2rem';
        case 'medium':
        default:
          return typeof sizeProp === 'number' ? `${(sizeProp / 16).toFixed(3)}rem` : '1.5rem';
      }
    }, [sizeProp]);

    return (
      <IconStyled ref={forwardedRef} {...rest}>
        <svg height={$size} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 16">
          <path
            fill="#fff"
            d="M5.806 8.97h2.097l-1.106 3.125c-.145.397.252.61.505.285L10.672 8a.4.4 0 0 0 .097-.247.255.255 0 0 0-.263-.262H8.404l1.11-3.124c.142-.398-.252-.61-.504-.282L5.639 8.462a.4.4 0 0 0-.1.246c0 .15.11.263.267.263M13.995 13.289c2.673-2.79 2.673-7.325 0-10.115a.55.55 0 0 0-.806 0 .61.61 0 0 0 0 .84c2.228 2.325 2.228 6.104 0 8.428a.61.61 0 0 0 0 .84.55.55 0 0 0 .406.174c.148 0 .291-.06.405-.173zm-1.407-2.11a4.24 4.24 0 0 0 1.17-2.95 4.24 4.24 0 0 0-1.17-2.95.55.55 0 0 0-.806 0 .61.61 0 0 0 0 .84c.537.56.834 1.31.834 2.11 0 .798-.297 1.543-.834 2.11a.61.61 0 0 0 0 .84c.114.119.257.173.406.173.148 0 .291-.06.405-.173zm-9.776 2.11a.61.61 0 0 0 0-.84c-2.229-2.325-2.229-6.104 0-8.428a.61.61 0 0 0 0-.84.55.55 0 0 0-.806 0C-.668 5.957-.668 10.498 2 13.288a.55.55 0 0 0 .406.172c.148 0 .291-.06.406-.172m1.407-2.11a.61.61 0 0 0 0-.84c-1.114-1.163-1.114-3.052 0-4.214a.61.61 0 0 0 0-.84.55.55 0 0 0-.806 0c-1.56 1.626-1.56 4.273 0 5.9a.55.55 0 0 0 .406.173c.148 0 .291-.06.405-.173z"
          />
        </svg>
      </IconStyled>
    );
  },
);

ActionServerLogo.defaultProps = {
  size: 'medium',
  color: 'inherit',
};
