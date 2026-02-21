/* istanbul ignore file */
import { StrictMode, lazy } from 'react';
import { createRoot } from 'react-dom/client';
import { setModuleFederationRemotesConfig } from '@internal-channels-components/import-helpers';
import { global } from '@internal-channels-components/theme';
import { initializeI18next } from '@internal-channels-components/i18n';

import { envVariables } from '#/shell/config/env';

import { locales } from './locales';
import { ChannelManagerProviderTemplate } from './config';
import { AppThemeProvider } from './theme';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';

// Initialize i18next
initializeI18next({
  resources: locales,
});

// Set Module Federation Remotes config from env variables
if (envVariables.REMOTES) {
  setModuleFederationRemotesConfig(envVariables.REMOTES);
}

const App = lazy(() => import('./App'));

const container = document.getElementById('root');
const root = createRoot(container!);

const debug = envVariables.REACT_APP_ENABLE_STRICT_MODE;

const Application = () => {
  return (
    <AppThemeProvider theme={global}>
      <ToastProvider>
        <ChannelManagerProviderTemplate>
          <AuthProvider>
            <App />
          </AuthProvider>
        </ChannelManagerProviderTemplate>
      </ToastProvider>
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
