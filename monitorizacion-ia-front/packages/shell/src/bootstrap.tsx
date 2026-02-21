/* istanbul ignore file */
import { StrictMode, lazy } from 'react';
import { createRoot } from 'react-dom/client';

import { envVariables } from '#/shell/config/env';

import { AppThemeProvider } from './theme';

const App = lazy(() => import('./App'));

const container = document.getElementById('root');
const root = createRoot(container!);

const debug = envVariables.REACT_APP_ENABLE_STRICT_MODE;

const Application = () => {
  return (
    <AppThemeProvider>
      <App />
    </AppThemeProvider>
  );
};

root.render(
  debug ? (
    <StrictMode>
      <Application />
    </StrictMode>
  ) : (
    <Application />
  ),
);
