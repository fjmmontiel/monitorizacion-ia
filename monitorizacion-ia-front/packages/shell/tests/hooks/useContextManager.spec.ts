import { renderHook, act } from '@testing-library/react';

import { useContextManager } from '../../src/hooks/useContextManager';
import contextService from '../../src/services/ContextService';
import { ContextItem } from '../../src/domains/Context.domain';
import { useToast } from '../../src/context/ToastContext';

jest.mock('../../src/services/ContextService');
jest.mock('../../src/context/ToastContext');

const mockItem = {
  id: 'item-1',
  name: 'Test Item',
  item_type: 'DataCliente',
  tab: '',
  llm_header: '',
  data: {},
};

describe('useContextManager', () => {
  const mockShowToast = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useToast as jest.Mock).mockReturnValue({ showToast: mockShowToast });
  });

  it('should subscribe to contextService and update items', () => {
    const mockSubscribe = jest.fn(listener => {
      listener([mockItem]);
      return () => {};
    });

    (contextService.subscribe as jest.Mock).mockImplementation(mockSubscribe);

    const { result } = renderHook(() => useContextManager());

    expect(result.current.items).toEqual([mockItem]);
    expect(mockSubscribe).toHaveBeenCalled();
  });

  it('should add a new item and show success toast', async () => {
    (contextService.getContextItem as jest.Mock).mockResolvedValue(mockItem);
    (contextService.updateContextItem as jest.Mock).mockImplementation(() => {
      contextService.emit('update', [mockItem]);
    });

    const { result } = renderHook(() => useContextManager());

    await act(async () => {
      await result.current.addItemToContext('item-1');
    });

    expect(contextService.getContextItem).toHaveBeenCalledWith('item-1');
    expect(contextService.updateContextItem).toHaveBeenCalledWith(mockItem);
    expect(mockShowToast).toHaveBeenCalledWith(
      expect.objectContaining({
        severity: expect.stringMatching(/success|info/),
        summary: expect.stringMatching(/Elemento (añadido|actualizado)/),
      }),
    );
  });

  it('should update an existing item and show info toast', async () => {
    const existingItem = new ContextItem({ ...mockItem, name: 'Old Name' });

    const mockSubscribe = jest.fn(listener => {
      listener([existingItem]);
      return () => {};
    });

    (contextService.subscribe as jest.Mock).mockImplementation(mockSubscribe);
    (contextService.getContextItem as jest.Mock).mockResolvedValue(mockItem);
    (contextService.updateContextItem as jest.Mock).mockImplementation(() => {
      contextService.emit('update', [mockItem]);
    });

    const { result } = renderHook(() => useContextManager());

    await act(async () => {
      await result.current.addItemToContext('item-1');
    });

    expect(mockShowToast).toHaveBeenCalledWith(
      expect.objectContaining({
        severity: 'info',
        summary: 'Elemento actualizado',
      }),
    );
  });

  it('should show error toast if getContextItem fails', async () => {
    (contextService.getContextItem as jest.Mock).mockRejectedValue(new Error('Not found'));

    const { result } = renderHook(() => useContextManager());

    await act(async () => {
      await result.current.addItemToContext('item-1');
    });

    expect(mockShowToast).toHaveBeenCalledWith(
      expect.objectContaining({
        severity: 'error',
        summary: 'Error',
        detail: expect.stringMatching(/Not found/),
      }),
    );
  });

  it('should delete item and show warning toast', () => {
    (contextService.deleteContextItem as jest.Mock).mockImplementation(() => {
      contextService.emit('update', []);
    });

    const { result } = renderHook(() => useContextManager());

    act(() => {
      result.current.deleteItemFromContext('item-1');
    });

    expect(contextService.deleteContextItem).toHaveBeenCalledWith('item-1');
    expect(mockShowToast).toHaveBeenCalledWith(
      expect.objectContaining({
        severity: 'warn',
        summary: 'Elemento eliminado',
      }),
    );
  });
});
