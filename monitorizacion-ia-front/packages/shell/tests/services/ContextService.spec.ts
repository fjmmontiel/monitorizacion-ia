import contextService from '../../src/services/ContextService';
import { ContextItem } from '../../src/domains/Context.domain';

const mockRawItem = {
  id: 'item-1',
  name: 'Test Item',
  item_type: 'DataCliente',
  data: {},
};

describe('ContextService', () => {
  beforeEach(() => {
    contextService.contextItems = [];
    jest.clearAllMocks();
  });

  it('should create a ContextItem instance', () => {
    const item = contextService.createContextItem(mockRawItem);
    expect(item).toBeInstanceOf(ContextItem);
    expect(item.id).toBe('item-1');
    expect(item.name).toBe('Test Item');
  });

  it('should update an existing item', () => {
    const item = contextService.createContextItem(mockRawItem);
    contextService.contextItems = [item];

    const updatedItem = contextService.createContextItem({ ...mockRawItem, name: 'Updated Name' });
    const listener = jest.fn();
    contextService.subscribe(listener);

    contextService.updateContextItem(updatedItem);

    expect(contextService.contextItems[0].name).toBe('Updated Name');
    expect(listener).toHaveBeenCalledWith([updatedItem]);
  });

  it('should add a new item if not found', () => {
    const item = contextService.createContextItem(mockRawItem);
    const listener = jest.fn();
    contextService.subscribe(listener);

    contextService.updateContextItem(item);

    expect(contextService.contextItems).toContainEqual(item);
    expect(listener).toHaveBeenCalledWith([item]);
  });

  it('should delete an item by ID', () => {
    const item = contextService.createContextItem(mockRawItem);
    contextService.contextItems = [item];

    const listener = jest.fn();
    contextService.subscribe(listener);

    contextService.deleteContextItem('item-1');

    expect(contextService.contextItems).toHaveLength(0);
    expect(listener).toHaveBeenCalledWith([]);
  });

  it('should not delete if item ID not found', () => {
    const item = contextService.createContextItem(mockRawItem);
    contextService.contextItems = [item];

    const listener = jest.fn();
    contextService.subscribe(listener);

    contextService.deleteContextItem('non-existent-id');

    expect(contextService.contextItems).toHaveLength(1);
    expect(listener).not.toHaveBeenCalledWith([]);
  });

  it('should subscribe and immediately notify with current items', () => {
    const item = contextService.createContextItem(mockRawItem);
    contextService.contextItems = [item];

    const listener = jest.fn();
    const unsubscribe = contextService.subscribe(listener);

    expect(listener).toHaveBeenCalledWith([item]);

    unsubscribe();
    contextService.updateContextItem(item); // should not trigger listener
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('should fetch context from API', async () => {
    const mockResponse = {
      items: [mockRawItem],
    };

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const items = await contextService.getContext();
    expect(items).toHaveLength(1);
    expect(items[0]).toBeInstanceOf(ContextItem);
    expect(items[0].id).toBe('item-1');
  });

  it('should fetch single context item from API', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => mockRawItem,
    });

    const item = await contextService.getContextItem('item-1');
    expect(item).toBeInstanceOf(ContextItem);
    expect(item?.id).toBe('item-1');
  });

  it('should throw error if getContextItem returns null', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => null,
    });

    await expect(contextService.getContextItem('item-1')).rejects.toThrow(/Item no encontrado/);
  });
});
