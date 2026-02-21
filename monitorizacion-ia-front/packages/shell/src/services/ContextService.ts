import { EventEmitter } from 'events';

import { customFetch } from '#/shell/services/CustomFetch';

import { ContextItem, ItemType } from '../domains/Context.domain';
import { envVariables } from '../config/env';

import { items_mock } from './items_mock';

const API_BASE_URL = envVariables.REACT_APP_API_URL;

// ContextService.ts
export class ContextService extends EventEmitter {
  private static instance: ContextService;
  contextItems: ContextItem<ItemType>[] = [];

  public static getInstance(): ContextService {
    if (!ContextService.instance) {
      ContextService.instance = new ContextService();
    }
    return ContextService.instance;
  }

  constructor() {
    super();
  }

  createContextItem<T extends ItemType>(raw: any): ContextItem<T> {
    return new ContextItem<T>(raw);
  }

  async getContext(): Promise<ContextItem<ItemType>[]> {
    const url = `${API_BASE_URL}/get-context`;
    const response = await customFetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const json = await response.json();
    if (json?.items) {
      this.contextItems = json.items.map((item: any) => this.createContextItem(item));
      return this.contextItems;
    }
    return [];
  }

  async getContextItem(id: string): Promise<ContextItem<ItemType> | null> {
    const url = `${API_BASE_URL}/contexto`;
    const response = await customFetch(`${url}?id=${encodeURIComponent(id)}&`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const json = await response.json();
    if (!json) {
      throw new Error(`Item no encontrado: ${id}`);
    }
    const contextItem = this.createContextItem(json);
    return contextItem;
  }

  async getContextItems(id: string): Promise<ContextItem<ItemType>[]> {
    let items = [];

    try {
      const url = `${API_BASE_URL}/contextoSesion`;
      const response = await customFetch(`${url}/${encodeURIComponent(id)}`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const jsonContextItems = await response.json();
      if (!jsonContextItems) {
        throw new Error(`Items de la sesión ${id} no encontrados.`);
      }

      items = jsonContextItems.map((i: any) => this.createContextItem(i));
    } catch (e) {
      items = JSON.parse(items_mock).map((i: any) => this.createContextItem(i));
      //throw new Error(`Error obteniendo el contexto de la sesión ${id}`);
    }

    return items;
  }

  updateContextItem(item: ContextItem<ItemType>) {
    const index = this.contextItems.findIndex(i => i.id === item.id);
    if (index !== -1) {
      this.contextItems = [...this.contextItems.slice(0, index), item, ...this.contextItems.slice(index + 1)];
    } else {
      this.contextItems = [...this.contextItems, item];
    }
    this.emit('update', this.contextItems);
  }

  deleteContextItem(id: string) {
    const index = this.contextItems.findIndex(item => item.id === id);
    if (index !== -1) {
      this.contextItems = [...this.contextItems.slice(0, index), ...this.contextItems.slice(index + 1)];
      this.emit('update', this.contextItems);
    }
  }

  reiniciarContexto() {
    this.contextItems = [];
    this.emit('update', this.contextItems);
  }

  subscribe(listener: (items: ContextItem<ItemType>[]) => void): () => void {
    this.on('update', listener);
    listener(this.contextItems);
    return () => {
      this.off('update', listener);
    };
  }
}

export default ContextService.getInstance();
