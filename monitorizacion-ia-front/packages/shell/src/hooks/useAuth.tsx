import { ReactNode, createContext, useCallback, useContext, useMemo, useState } from 'react';
const AuthContext = createContext<AuthContextProps | null>(null);

export interface AuthProps {
  username: string;
  token: string;
}

export interface AuthContextProps {
  user: AuthProps | null;
  login: (data: { username?: string; password?: string }) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthProps | null>(null);

  // call this function when you want to authenticate the user
  const login = ({ username, password }: { username?: string; password?: string }) => {
    const token = window.btoa(encodeURIComponent(password!));
    setUser({ username: username!, token });
  };

  // call this function to sign out logged in user
  const logout = () => {
    setUser(null);
  };

  const isAuthenticated = useCallback(() => {
    if (!user) {
      return false;
    }

    return !!user.token;
  }, [user]);

  const value = useMemo(
    () => ({
      user,
      login,
      logout,
      isAuthenticated,
    }),
    [user, isAuthenticated],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  return useContext(AuthContext);
};
