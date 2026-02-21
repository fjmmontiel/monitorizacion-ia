import { envVariables } from '#/shell/config/env';

export const customFetch = async (url: string, options: any) => {
  const headers = {
    ...options.headers,
    'X-Application-Id': envVariables.REACT_APP_CLIENT_ID,
    // Authorization: `Bearer ${token}`,
  };

  return fetch(url, {
    ...options,
    headers,
  });
};
