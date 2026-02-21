import { render, screen, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

import { envVariables } from '#/shell/config/env';

import { useAuth, AuthProvider, resetAuthSessionStorage } from '../../../src/context/AuthContext';

jest.mock('@internal-channels-components/auth', () => ({
  SsoAuth: jest.fn().mockImplementation(() => ({
    authorize: jest.fn(),
    requestAccessToken: jest.fn(),
    refreshAccessToken: jest.fn(),
    logout: jest.fn(),
  })),
  LdapAuth: jest.fn().mockImplementation(() => ({
    authorize: jest.fn(),
    postFormLDAP: jest.fn(),
    requestAccessToken: jest.fn(),
    refreshAccessToken: jest.fn(),
  })),
}));

jest.mock('#/shell/config/env', () => ({
  envVariables: {
    REACT_APP_AUTH_HOST: 'https://test-auth.example.com',
    REACT_APP_SSO_URI: '/sso',
    REACT_APP_LDAP_URI: '/ldap',
    REACT_APP_CLIENT_ID: 'test-client-id',
    REACT_APP_BASE_URL: 'https://test-app.example.com',
    REACT_APP_SKIP_AUTH: false,
  },
}));

const TestComponent = () => {
  const auth = useAuth();
  return (
    <div>
      <button onClick={auth.startSSOAuth} data-testid="sso-button">
        Start SSO
      </button>
      <button onClick={auth.startLDAPAuth} data-testid="ldap-button">
        Start LDAP
      </button>
      <button onClick={() => auth.sendLDAPForm('user', 'pass', 'nonce')} data-testid="ldap-form-button">
        Send LDAP Form
      </button>
      <button onClick={() => auth.requestAuthToken('test-code')} data-testid="request-token-button">
        Request Token
      </button>
      <button onClick={auth.startRefreshToken} data-testid="refresh-token-button">
        Start Refresh Token
      </button>
      <button onClick={() => auth.logout()} data-testid="logout-button">
        Logout
      </button>
      <div data-testid="is-authenticated">{auth.isAuthenticated() ? 'true' : 'false'}</div>
    </div>
  );
};

const TestComponentWithoutProvider = () => {
  try {
    useAuth();
    return <div>Should not render</div>;
  } catch (error) {
    return <div data-testid="error">{(error as Error).message}</div>;
  }
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('useAuth hook', () => {
    it('should throw error when used outside AuthProvider', () => {
      render(<TestComponentWithoutProvider />);
      expect(screen.getByTestId('error')).toHaveTextContent('Invalid authContext');
    });

    it('should provide auth context when used inside AuthProvider', () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      expect(screen.getByTestId('sso-button')).toBeInTheDocument();
      expect(screen.getByTestId('ldap-button')).toBeInTheDocument();
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
    });
  });

  describe('Authentication methods', () => {
    it('should start SSO authentication', () => {
      const { SsoAuth } = require('@internal-channels-components/auth');
      const mockAuthorize = jest.fn();
      SsoAuth.mockImplementation(() => ({
        authorize: mockAuthorize,
        requestAccessToken: jest.fn(),
        refreshAccessToken: jest.fn(),
        logout: jest.fn(),
      }));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      act(() => {
        screen.getByTestId('sso-button').click();
      });

      expect(sessionStorage.getItem('auth_flow')).toBe('sso');
      expect(mockAuthorize).toHaveBeenCalled();
    });

    it('should start LDAP authentication', () => {
      const { LdapAuth } = require('@internal-channels-components/auth');
      const mockAuthorize = jest.fn();
      LdapAuth.mockImplementation(() => ({
        authorize: mockAuthorize,
        postFormLDAP: jest.fn(),
        requestAccessToken: jest.fn(),
        refreshAccessToken: jest.fn(),
      }));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      act(() => {
        screen.getByTestId('ldap-button').click();
      });

      expect(sessionStorage.getItem('auth_flow')).toBe('ldap');
      expect(mockAuthorize).toHaveBeenCalled();
    });

    it('should send LDAP form', () => {
      const { LdapAuth } = require('@internal-channels-components/auth');
      const mockPostFormLDAP = jest.fn();
      LdapAuth.mockImplementation(() => ({
        authorize: jest.fn(),
        postFormLDAP: mockPostFormLDAP,
        requestAccessToken: jest.fn(),
        refreshAccessToken: jest.fn(),
      }));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      act(() => {
        screen.getByTestId('ldap-form-button').click();
      });

      expect(mockPostFormLDAP).toHaveBeenCalledWith('user', 'pass', 'nonce');
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when SKIP_AUTH is enabled', () => {
      const originalSkipAuth = envVariables.REACT_APP_SKIP_AUTH;
      (envVariables as any).REACT_APP_SKIP_AUTH = true;

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');

      (envVariables as any).REACT_APP_SKIP_AUTH = originalSkipAuth;
    });

    it('should return false when no auth flow is set', () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
    });

    it('should return true when all required session storage values are valid and tokens have not expired', () => {
      // Configuración de valores en sessionStorage
      sessionStorage.setItem('auth_flow', 'sso');
      sessionStorage.setItem('consented_on', `${Math.floor(Date.now() / 1000)}`); // Timestamp actual (en segundos)
      sessionStorage.setItem('expires_in', '3600'); // Token válido por 1 hora
      sessionStorage.setItem('refresh_token_expires_in', '7200'); // Refresh token válido por 2 horas

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      // Verifica que el componente muestre que el usuario está autenticado
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
    });
  });

  describe('requestAuthToken', () => {
    it('should handle SSO token request successfully', async () => {
      const { SsoAuth } = require('@internal-channels-components/auth');
      const mockRequestAccessToken = jest.fn().mockResolvedValue({
        consented_on: 1234567890,
        expires_in: 3600,
        scope: 'test-scope',
        refresh_token_expires_in: 7200,
        token_type: 'Bearer',
      });

      SsoAuth.mockImplementation(() => ({
        authorize: jest.fn(),
        requestAccessToken: mockRequestAccessToken,
        refreshAccessToken: jest.fn(),
        logout: jest.fn(),
      }));

      sessionStorage.setItem('auth_flow', 'sso');

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      await act(async () => {
        screen.getByTestId('request-token-button').click();
      });

      expect(mockRequestAccessToken).toHaveBeenCalledWith('test-code');
      expect(sessionStorage.getItem('consented_on')).toBe('1234567890');
      expect(sessionStorage.getItem('expires_in')).toBe('3600');
      expect(sessionStorage.getItem('scope')).toBe('test-scope');
      expect(sessionStorage.getItem('refresh_token_expires_in')).toBe('7200');
      expect(sessionStorage.getItem('token_type')).toBe('Bearer');
    });

    // it('should handle LDAP token request successfully', async () => {
    //   const { LdapAuth } = require('@internal-channels-components/auth');
    //   const mockRequestAccessToken = jest.fn().mockResolvedValue({
    //     consented_on: 1234567890,
    //     expires_in: 3600,
    //     scope: 'test-scope',
    //     refresh_token_expires_in: 7200,
    //     token_type: 'Bearer',
    //   });

    //   LdapAuth.mockImplementation(() => ({
    //     authorize: jest.fn(),
    //     postFormLDAP: jest.fn(),
    //     requestAccessToken: mockRequestAccessToken,
    //     refreshAccessToken: jest.fn(),
    //   }));

    //   sessionStorage.setItem('auth_flow', 'ldap');

    //   render(
    //     <AuthProvider>
    //       <TestComponent />
    //     </AuthProvider>,
    //   );

    //   await act(async () => {
    //     screen.getByTestId('request-token-button').click();
    //   });

    //   expect(mockRequestAccessToken).toHaveBeenCalledWith('test-code');
    //   expect(sessionStorage.getItem('consented_on')).toBe('1234567890');
    //   expect(sessionStorage.getItem('expires_in')).toBe('3600');
    // });

    it('should handle SSO token request failure', async () => {
      const { SsoAuth } = require('@internal-channels-components/auth');
      const mockRequestAccessToken = jest.fn().mockRejectedValue(new Error('Auth failed'));
      const mockLogout = jest.fn();

      SsoAuth.mockImplementation(() => ({
        authorize: jest.fn(),
        requestAccessToken: mockRequestAccessToken,
        refreshAccessToken: jest.fn(),
        logout: mockLogout,
      }));

      sessionStorage.setItem('auth_flow', 'sso');

      Object.defineProperty(window, 'location', {
        value: { replace: jest.fn() },
        writable: true,
      });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      await act(async () => {
        screen.getByTestId('request-token-button').click();
      });

      await waitFor(() => {
        expect(mockLogout).toHaveBeenCalled();
      });
    });

    it('should handle LDAP token request failure', async () => {
      const { LdapAuth } = require('@internal-channels-components/auth');
      const mockRequestAccessToken = jest.fn().mockRejectedValue(new Error('Auth failed'));

      LdapAuth.mockImplementation(() => ({
        authorize: jest.fn(),
        postFormLDAP: jest.fn(),
        requestAccessToken: mockRequestAccessToken,
        refreshAccessToken: jest.fn(),
      }));

      sessionStorage.setItem('auth_flow', 'ldap');

      Object.defineProperty(window, 'location', {
        value: { replace: jest.fn() },
        writable: true,
      });

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      await act(async () => {
        screen.getByTestId('request-token-button').click();
      });

      await waitFor(() => {
        expect(window.location.replace).toHaveBeenCalled();
      });
    });

    it('should handle unknown auth flow', async () => {
      sessionStorage.setItem('auth_flow', 'unknown');

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      await act(async () => {
        screen.getByTestId('request-token-button').click();
      });

      expect(screen.getByTestId('request-token-button')).toBeInTheDocument();
    });
  });

  describe('refresh token functionality', () => {
    it('should start refresh token for SSO', () => {
      sessionStorage.setItem('expires_in', '3600');
      sessionStorage.setItem('auth_flow', 'sso');

      const TestRefreshComponent = () => {
        const auth = useAuth();
        return (
          <button onClick={auth.startRefreshToken} data-testid="refresh-button">
            Refresh
          </button>
        );
      };

      render(
        <AuthProvider>
          <TestRefreshComponent />
        </AuthProvider>,
      );

      act(() => {
        screen.getByTestId('refresh-button').click();
      });

      expect(screen.getByTestId('refresh-button')).toBeInTheDocument();
    });

    it('should logout when refresh time is invalid', () => {
      sessionStorage.setItem('expires_in', 'invalid');

      Object.defineProperty(window, 'location', {
        value: { replace: jest.fn() },
        writable: true,
      });

      const TestRefreshComponent = () => {
        const auth = useAuth();
        return (
          <button onClick={auth.startRefreshToken} data-testid="refresh-button">
            Refresh
          </button>
        );
      };

      render(
        <AuthProvider>
          <TestRefreshComponent />
        </AuthProvider>,
      );

      act(() => {
        screen.getByTestId('refresh-button').click();
      });

      expect(window.location.replace).toHaveBeenCalled();
    });

    it('should logout when no refresh time is available', () => {
      Object.defineProperty(window, 'location', {
        value: { replace: jest.fn() },
        writable: true,
      });

      const TestRefreshComponent = () => {
        const auth = useAuth();
        return (
          <button onClick={auth.startRefreshToken} data-testid="refresh-button">
            Refresh
          </button>
        );
      };

      render(
        <AuthProvider>
          <TestRefreshComponent />
        </AuthProvider>,
      );

      act(() => {
        screen.getByTestId('refresh-button').click();
      });

      expect(window.location.replace).toHaveBeenCalled();
    });
  });

  describe('logout functionality', () => {
    it('should logout successfully', async () => {
      const { SsoAuth } = require('@internal-channels-components/auth');
      const mockLogout = jest.fn();

      SsoAuth.mockImplementation(() => ({
        authorize: jest.fn(),
        requestAccessToken: jest.fn(),
        refreshAccessToken: jest.fn(),
        logout: mockLogout,
      }));

      Object.defineProperty(window, 'location', {
        value: { replace: jest.fn() },
        writable: true,
      });

      sessionStorage.setItem('userInfo', 'test-user');
      sessionStorage.setItem('auth_flow', 'sso');

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      await act(async () => {
        screen.getByTestId('logout-button').click();
      });

      expect(mockLogout).toHaveBeenCalled();
      expect(window.location.replace).toHaveBeenCalledWith('https://test-app.example.com/login?choose=true');
    });

    it('should logout with auth error', async () => {
      const { SsoAuth } = require('@internal-channels-components/auth');
      const mockLogout = jest.fn();

      SsoAuth.mockImplementation(() => ({
        authorize: jest.fn(),
        requestAccessToken: jest.fn(),
        refreshAccessToken: jest.fn(),
        logout: mockLogout,
      }));

      Object.defineProperty(window, 'location', {
        value: { replace: jest.fn() },
        writable: true,
      });

      const TestLogoutComponent = () => {
        const auth = useAuth();
        return (
          <button onClick={() => auth.logout(true)} data-testid="logout-error-button">
            Logout with Error
          </button>
        );
      };

      render(
        <AuthProvider>
          <TestLogoutComponent />
        </AuthProvider>,
      );

      await act(async () => {
        screen.getByTestId('logout-error-button').click();
      });

      expect(mockLogout).toHaveBeenCalled();
      expect(window.location.replace).toHaveBeenCalledWith(
        'https://test-app.example.com/login?choose=true&authError=true',
      );
    });

    it('should clear refresh timer and reset variables during logout', async () => {
      const { SsoAuth } = require('@internal-channels-components/auth');
      const mockLogout = jest.fn();
      const mockRefreshAccessToken = jest.fn().mockResolvedValue({
        consented_on: Date.now(),
        expires_in: 3600,
        scope: 'test-scope',
        refresh_token_expires_in: 7200,
        token_type: 'Bearer',
      });

      SsoAuth.mockImplementation(() => ({
        authorize: jest.fn(),
        requestAccessToken: jest.fn(),
        refreshAccessToken: mockRefreshAccessToken,
        logout: mockLogout,
      }));

      Object.defineProperty(window, 'location', {
        value: { replace: jest.fn() },
        writable: true,
      });

      sessionStorage.setItem('auth_flow', 'sso');
      sessionStorage.setItem('expires_in', (Date.now() + 3600000).toString());
      sessionStorage.setItem('refresh_token_expires_in', (Date.now() + 7200000).toString());

      const TestRefreshComponent = () => {
        const auth = useAuth();
        return (
          <div>
            <button onClick={auth.startRefreshToken} data-testid="start-refresh-button">
              Start Refresh
            </button>
            <button onClick={() => auth.logout()} data-testid="logout-after-refresh-button">
              Logout
            </button>
          </div>
        );
      };

      render(
        <AuthProvider>
          <TestRefreshComponent />
        </AuthProvider>,
      );

      await act(async () => {
        screen.getByTestId('start-refresh-button').click();
      });

      await act(async () => {
        screen.getByTestId('logout-after-refresh-button').click();
      });

      expect(mockLogout).toHaveBeenCalled();
      expect(window.location.replace).toHaveBeenCalledWith('https://test-app.example.com/login?choose=true');
    });
  });

  describe('useEffect initialization', () => {
    it('should handle unknown auth flow in useEffect', () => {
      sessionStorage.setItem('auth_flow', 'unknown');

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>,
      );

      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
    });
  });

  describe('resetAuthSessionStorage', () => {
    it('should clear all auth-related session storage items', () => {
      sessionStorage.setItem('consented_on', '123');
      sessionStorage.setItem('expires_in', '3600');
      sessionStorage.setItem('scope', 'test');
      sessionStorage.setItem('refresh_token_expires_in', '7200');
      sessionStorage.setItem('token_type', 'Bearer');
      sessionStorage.setItem('auth_flow', 'sso');

      resetAuthSessionStorage();

      expect(sessionStorage.getItem('consented_on')).toBeNull();
      expect(sessionStorage.getItem('expires_in')).toBeNull();
      expect(sessionStorage.getItem('scope')).toBeNull();
      expect(sessionStorage.getItem('refresh_token_expires_in')).toBeNull();
      expect(sessionStorage.getItem('token_type')).toBeNull();
      expect(sessionStorage.getItem('auth_flow')).toBeNull();
    });
  });
});
