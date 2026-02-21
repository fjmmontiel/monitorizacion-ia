import { z } from 'zod';

const envVariablesSchema = z.object({
  REMOTES: z.record(z.string(), z.string()),
  REACT_APP_ENABLE_MOCKS: z
    .enum(['true', 'false'])
    .transform(value => value === 'true')
    .default('false'),
  REACT_APP_ENABLE_STRICT_MODE: z
    .enum(['true', 'false'])
    .transform(value => value === 'true')
    .default('false'),
  REACT_APP_SKIP_AUTH: z
    .enum(['true', 'false'])
    .transform(value => value === 'true')
    .default('false'),
  REACT_APP_SERVER_PROTOCOL: z.enum(['http', 'https']).default('http'),
  REACT_APP_MOCK_PORT_NUMBER: z.string().default('8080'),
  REACT_APP_CONFIG_FILE: z.string(),

  REACT_APP_AUTH_HOST: z.string().default('https://apis-nopr.unicajasc.corp/interno/desa-unicaja/portales-internos'),
  REACT_APP_SSO_URI: z.string().default('/sso/oauth2'),
  REACT_APP_LDAP_URI: z.string().default('/oauth2'),
  REACT_APP_CLIENT_ID: z.string().default('3ced262f21ceea16934a164589ae2ce2'),
  REACT_APP_BASE_URL: z.string().default('https://local.unicajasc.corp:3000'),
  REACT_APP_API_URL: z
    .string()
    .default('https://apis-nopr.unicajasc.corp/interno/inte-unicaja/ia/iag-frontales/hipotecas'),
  REACT_APP_SUBIR_FICHEROS: z
    .enum(['true', 'false'])
    .transform(value => value === 'true')
    .default('false'),
});

const parseEnvironmentVariables = () => {
  const env = envVariablesSchema.safeParse(process.env);
  if (!env.success) {
    // eslint-disable-next-line no-console
    console.error('Invalid environment variables, please check your .env file.', env.error);
    return {} as z.infer<typeof envVariablesSchema>;
  }

  return env.data;
};

export const envVariables = parseEnvironmentVariables();
