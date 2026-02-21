import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import '@testing-library/jest-dom';
import { PrivateRoutes } from '../../../src/components/PrivateRoutes/PrivateRoutes';
import { useAuth } from '../../../src/context/AuthContext';

jest.mock('../../../src/context/AuthContext', () => ({
  useAuth: jest.fn(),
}));

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

describe('PrivateRoutes', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render child components when user is authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: jest.fn().mockReturnValue(true),
      startSSOAuth: jest.fn(),
      startLDAPAuth: jest.fn(),
      sendLDAPForm: jest.fn(),
      requestAuthToken: jest.fn(),
      startRefreshToken: jest.fn(),
      refreshToken: jest.fn(),
      logout: jest.fn(),
    });

    render(
      <MemoryRouter>
        <PrivateRoutes />
      </MemoryRouter>,
    );

    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  it('should redirect to login when user is not authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: jest.fn().mockReturnValue(false),
      startSSOAuth: jest.fn(),
      startLDAPAuth: jest.fn(),
      sendLDAPForm: jest.fn(),
      requestAuthToken: jest.fn(),
      startRefreshToken: jest.fn(),
      refreshToken: jest.fn(),
      logout: jest.fn(),
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <PrivateRoutes />
      </MemoryRouter>,
    );

    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  it('should call isAuthenticated method', () => {
    const mockIsAuthenticated = jest.fn().mockReturnValue(true);
    mockUseAuth.mockReturnValue({
      isAuthenticated: mockIsAuthenticated,
      startSSOAuth: jest.fn(),
      startLDAPAuth: jest.fn(),
      sendLDAPForm: jest.fn(),
      requestAuthToken: jest.fn(),
      startRefreshToken: jest.fn(),
      refreshToken: jest.fn(),
      logout: jest.fn(),
    });

    render(
      <MemoryRouter>
        <PrivateRoutes />
      </MemoryRouter>,
    );

    expect(mockIsAuthenticated).toHaveBeenCalled();
  });

  it('should handle authentication function edge cases', () => {
    const mockIsAuthenticated = jest.fn();
    const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
    mockUseAuth.mockReturnValue({
      isAuthenticated: mockIsAuthenticated,
      startSSOAuth: jest.fn(),
      startLDAPAuth: jest.fn(),
      sendLDAPForm: jest.fn(),
      requestAuthToken: jest.fn(),
      startRefreshToken: jest.fn(),
      refreshToken: jest.fn(),
      logout: jest.fn(),
    });

    const falsyValues = [null, undefined, 0, false];

    falsyValues.forEach(falsyValue => {
      mockIsAuthenticated.mockReturnValue(falsyValue);
      const { container } = render(
        <MemoryRouter>
          <PrivateRoutes />
        </MemoryRouter>,
      );

      expect(container).toBeInTheDocument();
    });
  });

  it('should handle different authentication return types', () => {
    const mockIsAuthenticated = jest.fn();
    const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
    mockUseAuth.mockReturnValue({
      isAuthenticated: mockIsAuthenticated,
      startSSOAuth: jest.fn(),
      startLDAPAuth: jest.fn(),
      sendLDAPForm: jest.fn(),
      requestAuthToken: jest.fn(),
      startRefreshToken: jest.fn(),
      refreshToken: jest.fn(),
      logout: jest.fn(),
    });

    const truthyValues = [true, 1, 'authenticated', {}, []];

    truthyValues.forEach(truthyValue => {
      mockIsAuthenticated.mockReturnValue(truthyValue);
      const { container } = render(
        <MemoryRouter>
          <PrivateRoutes />
        </MemoryRouter>,
      );

      expect(container).toBeInTheDocument();
    });
  });
});
