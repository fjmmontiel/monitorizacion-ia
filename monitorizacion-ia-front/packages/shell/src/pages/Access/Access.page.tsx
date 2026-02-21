import { Navigate } from 'react-router-dom';

import { getRoutePath } from '#/shell/router/router.config';

export const AccessPage = () => {
  return <Navigate to={getRoutePath('chat')} />;
};

export const element = <AccessPage />;

export const loader = async () => {
  return {};
};
