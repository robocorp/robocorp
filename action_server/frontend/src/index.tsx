import { createRoot } from 'react-dom/client';
import { ActionServerRoot } from './components/ActionServerRoot';

const container = document.getElementById('root');

if (container) {
  const root = createRoot(container);
  root.render(<ActionServerRoot/>);
}
