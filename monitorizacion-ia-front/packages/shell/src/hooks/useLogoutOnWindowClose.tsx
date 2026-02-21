/* istanbul ignore file */
import { useEffect } from 'react';

import { useAuth } from '../context/AuthContext';

export function useLogoutOnWindowClose() {
  const { logout, isAuthenticated } = useAuth();

  // Rutas internas en las que NO queremos cerrar sesión al navegar entre ellas
  const INTERNAL_ALLOWED_ROUTES = ['/chat', '/sesion'];

  const AUTH_REDIRECT_FLAG = 'AUTH_REDIRECT_IN_PROGRESS';

  function isAuthRoute(href: string): boolean {
    return ['/auth', '/login'].some(p => href.includes(p));
  }

  function isInternalAllowedRoute(pathname: string): boolean {
    // Coincidencia exacta o prefijo (por si tienes subrutas como /chat/123)
    return INTERNAL_ALLOWED_ROUTES.some(p => pathname === p || pathname.startsWith(`${p}/`));
  }

  function isAuthRedirectInProgress(): boolean {
    try {
      return sessionStorage.getItem(AUTH_REDIRECT_FLAG) === 'TRUE';
    } catch {
      return false;
    }
  }

  useEffect(() => {
    const handleBeforeUnload = () => {
      try {
        safeLogout();
        return true;
      } catch {
        return false;
      }
    };

    const safeLogout = () => {
      // Evitar logout si hay redirección SSO en curso
      if (isAuthRedirectInProgress()) {
        return;
      }

      // 2) Evitar logout si estamos en rutas de auth
      const href = typeof document !== 'undefined' ? document.location.href : '';
      const pathname = typeof document !== 'undefined' ? document.location.pathname : '';

      // Evitar logout si navegamos hacia rutas de auth
      if (typeof document !== 'undefined' && isAuthRoute(href)) {
        return;
      }

      // 3) Evitar logout cuando estamos en rutas internas permitidas
      //    Esto es útil si, por alguna razón, el evento se dispara al cambiar de ruta.
      if (isInternalAllowedRoute(pathname)) {
        return;
      }

      logout(); // idealmente idempotente y rápido
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isAuthenticated, logout]);
}
