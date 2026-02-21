/* istanbul ignore file */
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { AppQueryParamsProvider } from '#/shell/hooks/AppQueryParamsContext';

export const ChatQueryParamsRoute: React.FC = () => {
  const { search } = useLocation();

  // Pasamos location.search para fijar los query params al montarse la ruta /chat.
  return (
    <AppQueryParamsProvider sourceSearch={search}>
      <Outlet />
    </AppQueryParamsProvider>
  );
};
