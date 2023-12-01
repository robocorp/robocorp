import { Content, Header, Panel } from '@robocorp/components';
import { FC } from 'react';

export const Welcome: FC<{}> = () => {
  return (
    <div>
      <Header>
        <Header.Title title="Welcome!"></Header.Title>
      </Header>
      <Content>
        <h3>How to use:</h3>
        <p>
          <strong>Import an action package from a directory</strong> (directory containing a{' '}
          <strong>conda.yaml</strong> and python modules with <strong>@action</strong>) with:
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
            <br/>
          Note: currently changes are not collected in real-time, the server must be restarted after
          importing actions and after a run the page must be manually rerfeshed.
        </p>
      </Content>
    </div>
  );
};
