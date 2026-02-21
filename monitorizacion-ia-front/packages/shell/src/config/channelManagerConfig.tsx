/* istanbul ignore file */
import { ChannelManagerProvider, ChannelManager, useChannelManager } from '@architecture-components/channel-manager';
import { ReactNode } from 'react';

import config from './index';

const channelManagerInstance = new ChannelManager({
  channel: { name: 'iagmvps-front-atencion-cliente', idChannel: '01' },
});

const ChannelManagerWrapper = ({ children }: { children: ReactNode }) => {
  const { channelManager } = useChannelManager();
  const { clientId, oauthRedirect, oauthConfirmationRedirect, oauthURI, scope } = config.login;
  channelManager.setEnvironment({
    apiHost: config.apiHost,
    wasHost: config.wasHost,
    apiInternalHost: config.apiInternalHost,
    oauthURI,
    oauthRedirect,
    oauthConfirmationRedirect,
    clientId,
    scope,
  });
  return <>{children}</>;
};

export const ChannelManagerProviderTemplate = ({ children }: { children: ReactNode }) => {
  return (
    <ChannelManagerProvider channelManager={channelManagerInstance}>
      <ChannelManagerWrapper>{children}</ChannelManagerWrapper>
    </ChannelManagerProvider>
  );
};
