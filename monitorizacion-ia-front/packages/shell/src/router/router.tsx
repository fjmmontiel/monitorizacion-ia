/* istanbul ignore file */
import { createBrowserRouter, Navigate, useRouteError } from 'react-router-dom';

import { PrivateRoutes } from '../components/PrivateRoutes/PrivateRoutes';
import { TopNavLayout } from '../layouts/TopNavLayout';
import { ChatQueryParamsRoute } from '../pages/Chat/ChatQueryParamsRoute';

import { getRoutePath } from './router.config';

const RootErrorBoundary = () => {
  const error = useRouteError();

  return (
    <>
      <div>Something went wrong. Check console for more information</div>
      <span>Error: {(error as Error).message}</span>
    </>
  );
};

// This will probabily come from a PostLogin process
// const userInfo = {
//   profileIcon: {
//     content: leo,
//     username: 'Ezequiel',
//     onAction: () => {
//       return '';
//     },
//   },
// };

export const router = createBrowserRouter([
  {
    path: getRoutePath('auth'),
    lazy: () => import('#/shell/pages/Auth/Auth.page'),
  },
  {
    element: <PrivateRoutes />,
    errorElement: <RootErrorBoundary />,
    children: [
      {
        path: '/',
        element: <Navigate to={getRoutePath('chat')} />,
      },
      {
        element: <TopNavLayout />,
        children: [
          {
            path: getRoutePath('chat'),
            element: <ChatQueryParamsRoute />,
            children: [
              {
                index: true,
                lazy: async () => {
                  const module = await import('#/shell/pages/Chat/Chat.page');
                  return { Component: module.default };
                },
              },
            ],
          },
          {
            path: getRoutePath('sessionList'),
            element: <TopNavLayout />,
            children: [{ index: true, lazy: () => import('#/shell/pages/SessionList/SessionList.page') }],
          },
          {
            path: getRoutePath('sessionDetail'),
            element: <ChatQueryParamsRoute />,
            children: [{ index: true, lazy: () => import('#/shell/pages/SessionDetails/SessionDetail.page') }],
          },
        ],
      },
    ],
  },
  {
    path: '*',
    lazy: () => import('#/shell/pages/NotFound/NotFound.page'),
  },
]);
