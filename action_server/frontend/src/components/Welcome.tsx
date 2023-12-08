import { Box, Content, Header, Panel } from '@robocorp/components';
import { FC } from 'react';

export const Welcome: FC<{}> = () => {
  return (
    <div style={{ marginLeft: '1em', marginRight: '1em' }}>
      <Header>
        <Header.Title title="Welcome!"></Header.Title>
      </Header>
      <Content>
        <h3>How to use:</h3>
        <p>
          <strong>Import an action package from a directory</strong> (directory containing a{' '}
          <code>conda.yaml</code> and python modules with <code>@action</code>) with:
          <br />
          <br />
          <code>python -m robocorp.action_server import -d directory</code>
        </p>
        <p>
          <br />
          <strong>Start the action server</strong> with:
          <br />
          <br />
          <code>python -m robocorp.action_server start</code>
        </p>
        <p>
          <br />
        </p>
      </Content>
    </div>
  );
};
