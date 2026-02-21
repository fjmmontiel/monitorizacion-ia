import '@testing-library/jest-dom';

import { renderHook, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { useAuth, AuthProvider } from '#/shell/hooks/useAuth';

const TestingUseAuth = () => {
  const auth = useAuth();
  return (
    <>
      {auth?.user?.token}
      {auth?.isAuthenticated() ? 'Authenticated' : 'Not authenticated'}
      <button onClick={() => auth?.login({ username: 'admin', password: 'test' })}>Login</button>
      <button onClick={() => auth?.logout()}>Logout</button>
    </>
  );
};

describe('useAuth()', () => {
  test('should do the login', async () => {
    render(
      <AuthProvider>
        <TestingUseAuth />
      </AuthProvider>,
    );

    await userEvent.click(screen.getByRole('button', { name: 'Login' }));
  });

  test('should do the logout', async () => {
    render(
      <AuthProvider>
        <TestingUseAuth />
      </AuthProvider>,
    );

    await userEvent.click(screen.getByRole('button', { name: 'Logout' }));
  });

  test('should initialize with current window size', () => {
    const { result } = renderHook(useAuth);
    expect(result.current).toEqual(null);
  });
});
