import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '#/shell/context/AuthContext';
import { getRoutePath } from '#/shell/router/router.config';

const AuthPage = () => {
  const { requestAuthToken, isAuthenticated } = useAuth();

  const navigate = useNavigate();
  const location = useLocation();
  const AUTH_REDIRECT_FLAG = 'AUTH_REDIRECT_IN_PROGRESS';

  useEffect(() => {
    const requestToken = async (code: string) => {
      await requestAuthToken(code);
      if (isAuthenticated()) {
        sessionStorage.setItem(AUTH_REDIRECT_FLAG, 'FALSE');
        const originalQuery = sessionStorage.getItem('hipotecas_query_string') || '';
        sessionStorage.removeItem('hipotecas_query_string');
        navigate(`${getRoutePath('chat')}${originalQuery}`);
      }
    };

    const checkCode = (params: URLSearchParams) => {
      const code = params.get('code');
      if (!code) {
        navigate(getRoutePath('chat'));
      } else {
        requestToken(code);
      }
    };

    const params = new URLSearchParams(location.search);
    checkCode(params);
  }, [location.search, navigate, isAuthenticated]);

  return <></>;
};

export const element = <AuthPage />;
