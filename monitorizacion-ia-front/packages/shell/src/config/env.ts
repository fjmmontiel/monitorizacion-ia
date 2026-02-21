import { z } from 'zod';

const envVariablesSchema = z.object({
  REMOTES: z.record(z.string(), z.string()).default({}),
  REACT_APP_ENABLE_STRICT_MODE: z
    .enum(['true', 'false'])
    .transform(value => value === 'true')
    .default('false'),
  MONITOR_API_BASE_URL: z.string().default('http://localhost:8002'),
  REACT_APP_MONITOR_MOCK_MODE: z
    .enum(['true', 'false'])
    .transform(value => value === 'true')
    .default('false'),
  REACT_APP_MONITOR_FAILOVER_TO_MOCK: z
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
