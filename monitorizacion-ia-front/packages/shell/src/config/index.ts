/* istanbul ignore file */
import { z } from 'zod';

import { envVariables } from '#/shell/config/env';

import { ChannelManagerProviderTemplate } from './channelManagerConfig';

export type EnvTypes = 'mock' | 'development' | 'integration' | 'production';
// TO DO: eliminar constante y realizar pruebas,
// o reconfigurar para que se utilice APP_ENVIRONMENT cuando no se especifique entorno en la tarea "npm run start"
const APP_ENVIRONMENT: EnvTypes = 'mock';

const ConfigSchema = z.object({
  apiHost: z.string(),
  wasHost: z.string(),
  apiInternalHost: z.string(),
  login: z.object({
    oauthURI: z.string().optional(),
    oauthRedirect: z.string(),
    oauthConfirmationRedirect: z.string(),
    clientId: z.string(),
    scope: z.string(),
  }),
});

export type Config = z.infer<typeof ConfigSchema>;

const getConfig = (): Config => {
  const config = envVariables.REACT_APP_CONFIG_FILE || APP_ENVIRONMENT;
  const configModule = require(`./${config}`);
  return ConfigSchema.parse(configModule.default);
};

export default getConfig();
export { ChannelManagerProviderTemplate };
