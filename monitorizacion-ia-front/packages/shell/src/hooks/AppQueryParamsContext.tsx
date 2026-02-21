import { createContext, useContext, useMemo, PropsWithChildren } from 'react';

type ParamsMap = Record<string, string | string[]>;

type AppQueryParamsApi = {
  all: ParamsMap;
  has: (key: string) => boolean;
  get: (key: string, fallback?: string | null) => string | string[] | null;
  getNumber: (key: string, fallback?: number | null) => number | null;
  getBoolean: (key: string, fallback?: boolean | null) => boolean | null;
  getArray: (key: string, fallback?: string[]) => string[];
};

const AppQueryParamsContext = createContext<AppQueryParamsApi | null>(null);

function parseQueryString(search: string): ParamsMap {
  const params = new URLSearchParams(search || '');
  const obj: ParamsMap = {};
  for (const [key, value] of params.entries()) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const prev = obj[key];
      if (Array.isArray(prev)) {
        prev.push(value);
        obj[key] = prev;
      } else {
        obj[key] = [prev, value];
      }
    } else {
      obj[key] = value;
    }
  }
  return obj;
}

type ProviderProps = PropsWithChildren<{
  /**
   * Optional search string to parse. If omitted the provider will attempt to use
   * window.location.search (safe-guarded for SSR).
   */
  sourceSearch?: string;
}>;

export function AppQueryParamsProvider({ children, sourceSearch }: ProviderProps) {
  const search =
    sourceSearch !== undefined ? sourceSearch : typeof window !== 'undefined' ? window.location.search : '';

  const params = useMemo(() => parseQueryString(search), [search]);

  const api = useMemo<AppQueryParamsApi>(
    () => ({
      all: params,
      has: (key: string) => Object.prototype.hasOwnProperty.call(params, key),
      get: (key: string, fallback: string | null = null) => {
        const v = params[key];
        if (v === undefined || v === 'undefined') {
          return fallback;
        }
        return v;
      },
      getNumber: (key: string, fallback: number | null = null) => {
        const v = params[key];
        if (v === undefined) {
          return fallback;
        }
        const raw = Array.isArray(v) ? v[0] : v;
        const n = Number(raw);
        return Number.isNaN(n) ? fallback : n;
      },
      getBoolean: (key: string, fallback: boolean | null = null) => {
        const v = params[key];
        if (v === undefined) {
          return fallback;
        }
        const s = (Array.isArray(v) ? v[0] : v).toLowerCase();
        if (s === 'true' || s === '1') {
          return true;
        }
        if (s === 'false' || s === '0') {
          return false;
        }
        return fallback;
      },
      getArray: (key: string, fallback: string[] = []) => {
        const v = params[key];
        if (v === undefined) {
          return fallback;
        }
        return Array.isArray(v) ? v : [v];
      },
    }),
    [params],
  );

  return <AppQueryParamsContext.Provider value={api}>{children}</AppQueryParamsContext.Provider>;
}

export function useAppQueryParams(): AppQueryParamsApi {
  const ctx = useContext(AppQueryParamsContext);
  if (!ctx) {
    throw new Error('useAppQueryParams must be used within AppQueryParamsProvider');
  }
  return ctx;
}
