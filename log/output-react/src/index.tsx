import { createRoot } from 'react-dom/client';
import { Log } from './Log';
import { setupGlobals } from './treebuild/setupWindowAPIs';

setupGlobals();

const container = document.getElementById('root');

if (container) {
  const root = createRoot(container);
  root.render(<Log />);
}
