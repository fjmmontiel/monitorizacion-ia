import ChatService, { ChatMessage } from '../../src/services/ChatService';

describe('ChatService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should create a user message', () => {
    const msg = ChatService.createUserMessage('hola');
    expect(msg).toHaveProperty('id');
    expect(msg.message).toBe('hola');
    expect(msg.role).toBe('user');
    expect(msg.timestamp).toBeInstanceOf(Date);
  });

  it('should handle HTTP error', async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: false, status: 500 });

    const messages: ChatMessage[] = [ChatService.createUserMessage('Hola?')];
    const onChunk = jest.fn();
    const onDone = jest.fn();
    const onError = jest.fn();

    await ChatService.sendMessage(messages, onChunk, onDone, onError, '');

    expect(onChunk).not.toHaveBeenCalled();
    expect(onDone).not.toHaveBeenCalled();
    expect(onError).toHaveBeenCalled();
    expect(onError.mock.calls[0][0].message).toMatch(/Error HTTP/);
  });

  it('should cancel request and close connection', () => {
    // @ts-ignore
    ChatService.controller = { abort: jest.fn() };
    // @ts-ignore
    ChatService.eventSource = { close: jest.fn() };
    ChatService.cancelRequest();
    // @ts-ignore
    expect(ChatService.controller).toBeNull();
    // @ts-ignore
    expect(ChatService.eventSource).toBeNull();
  });
});

describe('extractValidLines', () => {
  it("should extract lines starting with 'data:'", () => {
    const input = 'data: {"chunk":"hola"}\n\ndata: {"chunk":"mundo"}\n\n';
    const result = ChatService.extractValidLines(input);
    expect(result).toEqual(['data: {"chunk":"hola"}', 'data: {"chunk":"mundo"}']);
  });

  it("should ignore lines without 'data:'", () => {
    const input = '\n\nfoo\n\ndata: {"chunk":"hola"}\n\n';
    const result = ChatService.extractValidLines(input);
    expect(result).toEqual(['data: {"chunk":"hola"}']);
  });
});

describe('isContextEvent', () => {
  it('should detect valid context events', () => {
    expect(ChatService.isContextEvent('[ADD_CONTEXT=id123]')).toBe(true);
    expect(ChatService.isContextEvent('[REMOVE_CONTEXT=id123]')).toBe(true);
    expect(ChatService.isContextEvent('[UPDATE_CONTEXT=id123]')).toBe(true);
  });

  it('should ignore non-context chunks', () => {
    expect(ChatService.isContextEvent('Hola mundo')).toBe(false);
    expect(ChatService.isContextEvent('[UNKNOWN_CONTEXT=id123]')).toBe(false);
  });
});

describe('extractItemId', () => {
  it('should extract item ID correctly', () => {
    const chunk = '[ADD_CONTEXT=id456]';
    const result = ChatService.extractItemId(chunk);
    expect(result).toBe('id456');
  });

  it('should extract item ID correctly 2', () => {
    const chunk = '[ADD_CONTEXT=id456';
    const result = ChatService.extractItemId(chunk);
    expect(result).toBe('id456');
  });

  it('should extract item ID correctly 3', () => {
    const chunk = 'ADD_CONTEXT=id456]';
    const result = ChatService.extractItemId(chunk);
    expect(result).toBe('id456');
  });

  it('should extract item ID correctly 4', () => {
    const chunk = 'ADD_CONTEXT=id456';
    const result = ChatService.extractItemId(chunk);
    expect(result).toBe('id456');
  });

  it('should return undefined for malformed chunk', () => {
    const chunk = '[ADD_CONTEXT]';
    const result = ChatService.extractItemId(chunk);
    expect(result).toBeUndefined();
  });
});

describe('extractSessionId', () => {
  it('should extract session ID correctly', () => {
    const chunk = '[ID_SESION=abc123]';
    const result = ChatService.extractSessionId(chunk);
    expect(result).toBe('abc123');
  });

  it('should return null if session ID is missing', () => {
    const chunk = '[SOMETHING_ELSE=xyz]';
    const result = ChatService.extractSessionId(chunk);
    expect(result).toBeNull();
  });
});

describe('handleContextEvent', () => {
  it('should return correct event object for ADD_CONTEXT', () => {
    const result = ChatService.handleContextEvent('[ADD_CONTEXT=item1]', 'item1');
    expect(result).toEqual({ type: 'add', itemId: 'item1' });
  });

  it('should return correct event object for ADD_CONTEXT 1', () => {
    const result = ChatService.handleContextEvent('[ADD_CONTEXT=item1', 'item1');
    expect(result).toEqual({ type: 'add', itemId: 'item1' });
  });

  it('should return correct event object for ADD_CONTEXT 2', () => {
    const result = ChatService.handleContextEvent('ADD_CONTEXT=item1]', 'item1');
    expect(result).toEqual({ type: 'add', itemId: 'item1' });
  });

  it('should return correct event object for ADD_CONTEXT 3', () => {
    const result = ChatService.handleContextEvent('ADD_CONTEXT=item1', 'item1');
    expect(result).toEqual({ type: 'add', itemId: 'item1' });
  });

  it('should return correct event object for UPDATE_CONTEXT', () => {
    const result = ChatService.handleContextEvent('[UPDATE_CONTEXT=item2]', 'item2');
    expect(result).toEqual({ type: 'update', itemId: 'item2' });
  });

  it('should return correct event object for REMOVE_CONTEXT', () => {
    const result = ChatService.handleContextEvent('[REMOVE_CONTEXT=item3]', 'item3');
    expect(result).toEqual({ type: 'remove', itemId: 'item3' });
  });

  it('should return null for unknown event', () => {
    const result = ChatService.handleContextEvent('[UNKNOWN_CONTEXT=item4]', 'item4');
    expect(result).toBeNull();
  });
});

describe('processLine', () => {
  it("should call onDone if data.done is '[DONE]'", () => {
    const line = 'data: {"done":"[DONE]"}';
    const onDone = jest.fn();
    ChatService.processLine(line, jest.fn(), onDone);
    expect(onDone).toHaveBeenCalled();
  });

  it('should call onChunk if data.chunk is present', () => {
    const line = 'data: {"chunk":"Hola"}';
    const onChunk = jest.fn();
    ChatService.processLine(line, onChunk, jest.fn());
    expect(onChunk).toHaveBeenCalledWith('Hola');
  });
});

describe('processChunk', () => {
  const mockOnChunk = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should emit CONTEXT_EVENT if handleContextEvent returns an object', () => {
    const chunk = '[ADD_CONTEXT=item123]';
    const contextEvent: {
      type: 'add' | 'update' | 'remove';
      itemId: string;
    } | null = { type: 'add', itemId: 'item123' };

    jest.spyOn(ChatService, 'isContextEvent').mockReturnValue(true);
    jest.spyOn(ChatService, 'extractItemId').mockReturnValue('item123');
    jest.spyOn(ChatService, 'handleContextEvent').mockReturnValue(contextEvent);

    ChatService.processChunk(chunk, mockOnChunk);

    expect(mockOnChunk).toHaveBeenCalledWith(`[CONTEXT_EVENT]${JSON.stringify(contextEvent)}`);
  });

  it('should process normal chunk and call onChunk', () => {
    const chunk = 'Hola mundo';
    jest.spyOn(ChatService, 'isContextEvent').mockReturnValue(false);

    ChatService.processChunk(chunk, mockOnChunk);

    expect(mockOnChunk).toHaveBeenCalledWith('Hola mundo');
  });

  it('should extract and store session ID', () => {
    const chunk = '[ID_SESION=abc123]';
    jest.spyOn(ChatService, 'isContextEvent').mockReturnValue(false);
    jest.spyOn(ChatService, 'isSessionEvent').mockReturnValue(true);
    jest.spyOn(ChatService, 'extractSessionId').mockReturnValue('abc123');

    ChatService.processChunk(chunk, mockOnChunk);

    expect(ChatService['sessionId']).toBe('abc123');
  });
});
