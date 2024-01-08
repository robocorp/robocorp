import { FC, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

type Props = {
  path: string;
};

export const Redirect: FC<Props> = ({ path }) => {
  const navigate = useNavigate();

  useEffect(() => {
    navigate(path);
  }, []);

  return null;
};
