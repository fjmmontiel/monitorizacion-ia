/* istanbul ignore file */
export const routesConfig = {
  chat: {
    path: '/chat',
  },
  auth: {
    path: '/auth',
  },
  sessionList: {
    path: '/sesiones',
  },
  sessionDetail: {
    path: '/sesion/:id',
  },
};

export const getRoutePath = (route: keyof typeof routesConfig) => routesConfig[route].path;
