// useContextManager.ts
import { useEffect, useState } from 'react';

import contextService from '../services/ContextService';
import { ContextItem, ItemType } from '../domains/Context.domain';
import { useToast } from '../context/ToastContext';

export const useContextManager = () => {
  const [items, setItems] = useState<ContextItem<ItemType>[]>([]);
  const { showToast } = useToast();

  useEffect(() => {
    const unsubscribe = contextService.subscribe(setItems);
    return () => unsubscribe();
  }, []);

  const addItemToContext = async (id: string) => {
    try {
      const item = await contextService.getContextItem(id);
      if (item) {
        contextService.updateContextItem(item);
        const exists = items.some(i => i.id === id);
        if (item.itemType !== 'DataCliente' && item.itemType !== 'DataGestor') {
          showToast({
            severity: exists ? 'info' : 'success',
            life: 3000,
            detail: `El elemento ${item.name} ha sido ${exists ? 'actualizado' : 'añadido'} al panel del contexto.`,
            summary: exists ? 'Elemento actualizado' : 'Elemento añadido',
            sticky: false,
            position: 'bottom-center',
          });
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : typeof err === 'string' ? err : JSON.stringify(err);
      showToast({
        severity: 'error',
        life: 3000,
        detail: `Error al añadir el elemento: ${msg}`,
        summary: 'Error',
        sticky: false,
        position: 'bottom-center',
      });
    }
  };

  const deleteItemFromContext = (id: string) => {
    contextService.deleteContextItem(id);
    showToast({
      severity: 'warn',
      life: 3000,
      detail: `El elemento ha sido eliminado del contexto.`,
      summary: 'Elemento eliminado',
      sticky: false,
      position: 'bottom-center',
    });
  };

  const reiniciarContexto = () => {
    setItems([]);
  };

  const setSesionItems = (sesionItems: ContextItem<ItemType>[]) => {
    setItems(sesionItems);
  };

  return {
    items,
    setSesionItems,
    addItemToContext,
    deleteItemFromContext,
    reiniciarContexto,
  };
};
