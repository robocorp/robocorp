import { createRoot } from 'react-dom/client';
import { ActionServer } from './components/ActionServer';

const container = document.getElementById('root');

if (container) {
  const root = createRoot(container);
  // root.render(<p>Add content here</p>);
  root.render(<ActionServer/>);
}
