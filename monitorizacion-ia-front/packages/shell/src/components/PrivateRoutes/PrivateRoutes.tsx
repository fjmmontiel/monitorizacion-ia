import { Outlet } from 'react-router-dom';

import { useAuth } from '../../context/AuthContext';

export const PrivateRoutes = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated()) {
    return <div></div>;
  }
  return <Outlet />;
};
