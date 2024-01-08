/* eslint-disable styled-components-a11y/no-static-element-interactions */
/* eslint-disable styled-components-a11y/click-events-have-key-events */
import { Box, Typography } from '@robocorp/components';
import { Color, styled } from '@robocorp/theme';

const Card = styled.div<{ $color: Color }>`
  position: relative;
  border-radius: ${({ theme }) => theme.radii.$24};
  padding-bottom: ${({ theme }) => theme.space.$16};

  ${({ theme }) => theme.screen.s} {
    padding-bottom: ${({ theme }) => theme.space.$8};
  }

  > * {
    position: relative;
    z-index: 2;
  }

  a p {
    color: ${({ theme }) => theme.colors.content.subtle.light.color};
  }

  .thumbs {
    transition: transform 180ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  &:before {
    content: '';
    position: absolute;
    top: 0px;
    left: 0px;
    width: 100%;
    height: 100%;
    background: ${({ $color, theme }) => theme.color($color)};
    border-radius: ${({ theme }) => theme.radii.$24};
    box-shadow: 0px 0px 0px 4px ${({ $color, theme }) => theme.color($color)};
    transform: scale(0.8);
    opacity: 0;
    z-index: 1;
    transition:
      transform 240ms cubic-bezier(0.4, 0, 0.2, 1),
      opacity 240ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  &:hover {
    &:before {
      transform: scale(1);
      opacity: 1;
      transition:
        transform 180ms cubic-bezier(0.4, 0, 0.2, 1),
        opacity 160ms cubic-bezier(0.4, 0, 0.2, 1);
    }

    a strong {
      color: ${({ theme }) =>
        theme.name === 'dark' ? 'white' : theme.colors.content.primary.color};
    }

    a p {
      color: ${({ theme }) =>
        theme.name === 'dark' ? 'white' : theme.colors.content.primary.color};
    }

    .thumbs {
      transform: scale(1.05);
      transition: transform 200ms cubic-bezier(0.4, 0, 0.2, 1);
    }

    .badge {
      color: ${({ theme }) => theme.color('grey100', 'grey100')};
      background: ${({ theme }) => theme.color('grey0', 'grey0')};
    }
  }
`;

const ProcessCard = styled(Box)`
  color: ${({ theme }) => theme.colors.content.primary.color};
  text-decoration: none !important;
  border-radius: ${({ theme }) => theme.radii.$24};
  padding-bottom: ${({ theme }) => theme.space.$32};
  display: block;
  cursor: pointer;
`;

const Thumbs = styled.div<{ $color: Color }>`
  background: ${({ $color, theme }) => theme.color($color)}};
  border-radius: ${({ theme }) => theme.radii.$24};
  padding: 0 ${({ theme }) => theme.space.$32};
  margin-bottom: ${({ theme }) => theme.sizes.$24};

  > div {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 180px;
    color: ${({ theme }) => theme.colors.content.primary.color};
  }
`;

export const Thumb = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 70px;
  aspect-ratio: 1;
  border-radius: 88px;
  background: white;
  transform: scale(1.2);

  img {
    height: 65%;
    width: auto;
  }
`;

export const OnboardingCard = ({
  onClick,
  thumbnailColor,
  icon,
  title,
  description,
  ...rest
}: {
  onClick: () => void;
  thumbnailColor: Color;
  icon: React.ReactNode;
  title: string;
  description: string;
}) => {
  return (
    <Card $color={thumbnailColor} onClick={onClick} {...rest}>
      <ProcessCard>
        <Thumbs $color={thumbnailColor}>
          <div className="thumbs">
            <Thumb key="uptimeMonitoring">{icon}</Thumb>
          </div>
        </Thumbs>
        <Box px="$16" mb="$24">
          <Typography
            truncate={2}
            as="strong"
            my="$8"
            variant="display.headline"
            color="content.primary"
          >
            {title}
          </Typography>

          <Typography truncate={4} as="p" variant="body.small-loose" color="content.subtle.light">
            {description}
          </Typography>
        </Box>
      </ProcessCard>
    </Card>
  );
};
