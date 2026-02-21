import React, { createContext, ReactNode, useContext, useEffect, useRef } from 'react';
import { LdapAuth, SsoAuth } from '@internal-channels-components/auth';

import { envVariables } from '#/shell/config/env';

interface AuthContextType {
  startSSOAuth: () => void;
  startLDAPAuth: () => void;
  isAuthenticated: () => boolean;
  sendLDAPForm: (username: string, password: string, stateNonce: string) => void;
  requestAuthToken: (code: string) => Promise<void>;
  startRefreshToken: () => void;
  logout: (authError?: boolean) => void;
  refreshToken: (type: string) => void;
  //runRefreshToken: (type: 'sso' | 'ldap', refreshTime: number) => void;
}

const AUTH_REDIRECT_FLAG = 'AUTH_REDIRECT_IN_PROGRESS';
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('Invalid authContext');
  }
  return context;
};

interface AuthContextProps {
  children: ReactNode;
}

// eslint-disable-next-line react/prop-types
export const AuthProvider: React.FC<AuthContextProps> = ({ children }) => {
  const authMode = useRef<'sso' | 'ldap' | null>(null);
  const refreshTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const tokenExpiration = useRef<number | null>(null);
  const refreshTokenExpiration = useRef<number | null>(null);

  const ssoAuth = useRef(
    new SsoAuth({
      baseURL: envVariables.REACT_APP_AUTH_HOST,
      oauthURI: envVariables.REACT_APP_SSO_URI,
      clientId: envVariables.REACT_APP_CLIENT_ID,
      redirectUri: `${envVariables.REACT_APP_BASE_URL}/auth`,
      scope: 'iag-hipotecas',
      tokenViaCookie: true,
    }),
  );

  const ldapAuth = useRef(
    new LdapAuth({
      baseURL: envVariables.REACT_APP_AUTH_HOST,
      oauthURI: envVariables.REACT_APP_LDAP_URI,
      clientId: envVariables.REACT_APP_CLIENT_ID,
      redirectUri: `${envVariables.REACT_APP_BASE_URL}/ldap`,
      scope: 'iag-hipotecas',
      tokenViaCookie: true,
    }),
  );

  const startSSOAuth = () => {
    const currentQuery = window.location.search;
    sessionStorage.setItem('hipotecas_query_string', currentQuery);
    sessionStorage.setItem('auth_flow', 'sso');
    sessionStorage.setItem(AUTH_REDIRECT_FLAG, 'TRUE');
    ssoAuth.current.authorize();
  };

  const startLDAPAuth = () => {
    sessionStorage.setItem('auth_flow', 'ldap');
    sessionStorage.setItem(AUTH_REDIRECT_FLAG, 'TRUE');
    ldapAuth.current.authorize();
  };

  const isAuthenticated = () => {
    // Si se indica que se debe omitir la autenticación, retorna 'true'
    if (envVariables.REACT_APP_SKIP_AUTH) {
      return true;
    }

    // Obtén los valores necesarios desde sessionStorage
    const authFlow = sessionStorage.getItem('auth_flow');
    const consentedOn = sessionStorage.getItem('consented_on'); // Timestamp de cuándo se generaron los tokens
    const tokenExp = sessionStorage.getItem('expires_in'); // Tiempo de vida del token en segundos
    const refTokenExp = sessionStorage.getItem('refresh_token_expires_in'); // Tiempo de vida del refresh token en segundos

    // Verifica si existen todas las variables necesarias
    if (!authFlow || !consentedOn || !tokenExp || !refTokenExp) {
      startSSOAuth();
      return false;
    }

    // Calcula las fechas de expiración basadas en consented_on
    const consentedTime = parseInt(consentedOn, 10); // Momento en que se generaron los tokens (en segundos)
    const tokenExpirationTime = consentedTime + parseInt(tokenExp, 10); // Tiempo absoluto de expiración del token
    const refreshTokenExpirationTime = consentedTime + parseInt(refTokenExp, 10); // Tiempo absoluto de expiración del refresh token

    // Obtén el tiempo actual en segundos
    const now = Math.floor(Date.now() / 1000);

    // Verifica si el token o el refresh token han expirado
    if (now >= tokenExpirationTime) {
      startSSOAuth();
      return false;
    }

    if (now >= refreshTokenExpirationTime) {
      startSSOAuth();
      return false;
    }

    // Si todo está correcto, el usuario está autenticado
    return true;
  };

  const sendLDAPForm = (username: string, password: string, stateNonce: string) => {
    ldapAuth.current.postFormLDAP(username, password, stateNonce);
  };

  const requestAuthToken = async (code: string) => {
    switch (sessionStorage.getItem('auth_flow')) {
      case 'sso':
        try {
          authMode.current = 'sso';

          const resSso = await ssoAuth.current.requestAccessToken(code);

          sessionStorage.setItem('consented_on', resSso.consented_on.toString());
          sessionStorage.setItem('expires_in', resSso.expires_in.toString());
          sessionStorage.setItem('scope', resSso.scope);
          sessionStorage.setItem('refresh_token_expires_in', resSso.refresh_token_expires_in.toString());
          sessionStorage.setItem('token_type', resSso.token_type);

          tokenExpiration.current = resSso.expires_in;
          refreshTokenExpiration.current = resSso.refresh_token_expires_in;

          startRefreshToken();
        } catch {
          logout(true);
        }

        break;

      // case 'ldap':
      //   try {
      //     authMode.current = 'ldap';

      //     const resLdap = await ldapAuth.current.requestAccessToken(code);

      //     sessionStorage.setItem('consented_on', resLdap.consented_on.toString());
      //     sessionStorage.setItem('expires_in', resLdap.expires_in.toString());
      //     sessionStorage.setItem('scope', resLdap.scope);
      //     sessionStorage.setItem('refresh_token_expires_in', resLdap.refresh_token_expires_in.toString());
      //     sessionStorage.setItem('token_type', resLdap.token_type);

      //     tokenExpiration.current = resLdap.expires_in;
      //     refreshTokenExpiration.current = resLdap.refresh_token_expires_in;

      //     startRefreshToken();
      //   } catch {
      //     logout(true);
      //   }

      //   break;

      default:
        break;
    }
  };

  const startRefreshToken = () => {
    const refreshTime = sessionStorage.getItem('expires_in');

    if (!refreshTime || isNaN(parseInt(refreshTime))) {
      logout(true);
      return;
    }

    // refreshTime comes in seconds, multiply by 1000 to convert to milliseconds, then substract 5 seconds to prevent expired token
    switch (authMode.current) {
      case 'sso':
        runRefreshToken('sso', (Number(refreshTime) - 5) * 1000);
        break;

      case 'ldap':
        runRefreshToken('ldap', (Number(refreshTime) - 5) * 1000);
        break;

      default:
        break;
    }
  };

  const runRefreshToken = (type: 'sso' | 'ldap', refreshTime: number) => {
    if (refreshTimer.current) {
      clearInterval(refreshTimer.current);
      refreshTimer.current = null;
    }

    refreshTimer.current = setInterval(async () => {
      if (!tokenExpiration.current) {
        return;
      }

      await refreshToken(type);
    }, refreshTime);
  };

  const refreshToken = async (type: string) => {
    const response =
      type === 'sso' ? await ssoAuth.current.refreshAccessToken() : await ldapAuth.current.refreshAccessToken();
    sessionStorage.setItem('consented_on', response.consented_on.toString());
    sessionStorage.setItem('expires_in', response.expires_in.toString());
    sessionStorage.setItem('scope', response.scope);
    sessionStorage.setItem('refresh_token_expires_in', response.refresh_token_expires_in.toString());
    sessionStorage.setItem('token_type', response.token_type);
  };

  const resetVariables = () => {
    refreshTimer.current = null;
    authMode.current = null;
    tokenExpiration.current = null;
    refreshTokenExpiration.current = null;
  };

  const logout = async (authError = false) => {
    try {
      if (refreshTimer.current) clearInterval(refreshTimer.current);

      resetVariables();
      resetAuthSessionStorage();

      ssoAuth.current.logout();

      window.location.replace(
        `${envVariables.REACT_APP_BASE_URL}/login?choose=true${authError ? '&authError=true' : ''}`,
      );
    } catch (error) {
      throw new Error(`Error during logout: ${error}`);
    }
  };

  useEffect(() => {
    const authFlow = sessionStorage.getItem('auth_flow');
    const tokenExp = sessionStorage.getItem('expires_in');
    const refTokenExp = sessionStorage.getItem('refresh_token_expires_in');
    switch (authFlow) {
      case 'sso':
        authMode.current = 'sso';
        if (refTokenExp && tokenExp) {
          refreshTokenExpiration.current = Number(refTokenExp);
          tokenExpiration.current = Number(tokenExp);
          startRefreshToken();
        }
        break;

      // case 'ldap':
      //   authMode.current = 'ldap';
      //   if (refTokenExp && tokenExp) {
      //     refreshTokenExpiration.current = Number(refTokenExp);
      //     tokenExpiration.current = Number(tokenExp);
      //     startRefreshToken();
      //   }
      //   break;

      default:
        break;
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        startSSOAuth,
        startLDAPAuth,
        isAuthenticated,
        sendLDAPForm,
        requestAuthToken,
        startRefreshToken,
        logout,
        refreshToken,
      }}>
      {children}
    </AuthContext.Provider>
  );
};

export const resetAuthSessionStorage = () => {
  sessionStorage.removeItem('consented_on');
  sessionStorage.removeItem('expires_in');
  sessionStorage.removeItem('scope');
  sessionStorage.removeItem('refresh_token_expires_in');
  sessionStorage.removeItem('token_type');
  sessionStorage.removeItem('auth_flow');
  sessionStorage.removeItem(AUTH_REDIRECT_FLAG);
};
