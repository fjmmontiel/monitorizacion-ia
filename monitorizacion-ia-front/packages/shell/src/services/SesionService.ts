import { customFetch } from '#/shell/services/CustomFetch';

import { ContextItem, ItemType } from '../domains/Context.domain';
import { envVariables } from '../config/env';
import { SesionSortAndFilterOptions } from '../domains/Sesion.domain';

const API_BASE_URL = envVariables.REACT_APP_API_URL;

// SesionService.ts
export class SesionService {
  private static instance: SesionService;
  contextItems: ContextItem<ItemType>[] = [];

  public static getInstance(): SesionService {
    if (!SesionService.instance) {
      SesionService.instance = new SesionService();
    }
    return SesionService.instance;
  }

  public async getSesiones(options: SesionSortAndFilterOptions): Promise<[] | null> {
    let sesiones = null;
    try {
      const url = `${API_BASE_URL}/sesiones`;
      const response = await customFetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(options),
      });
      sesiones = await response.json();
      if (!sesiones) {
        throw new Error(`No se han encontrado sesiones`);
      }
    } catch (e) {
      throw new Error(`Error obteniendo sesiones`);
    }

    return sesiones;
  }
}

export default SesionService.getInstance();
