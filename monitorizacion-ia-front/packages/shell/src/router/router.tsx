/* istanbul ignore file */
import { Navigate, createBrowserRouter } from 'react-router-dom';

export const router = createBrowserRouter([
  {
    path: '/home',
    lazy: async () => {
      const module = await import('#/shell/features/home/pages/Home.page');
      return { Component: module.default };
    },
  },
  {
    path: '/monitor',
    lazy: async () => {
      const module = await import('#/shell/features/monitor/pages/MonitorDashboard.page');
      return { Component: module.default };
    },
  },
  {
    path: '/',
    element: <Navigate to='/home' replace />,
  },
  {
    path: '*',
    element: <Navigate to='/home' replace />,
  },
]);
