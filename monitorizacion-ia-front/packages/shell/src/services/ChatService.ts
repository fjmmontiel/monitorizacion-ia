import { customFetch } from '#/shell/services/CustomFetch';

import { envVariables } from '../config/env';

export interface ChatMessage {
  id: string;
  message: string;
  role: 'user' | 'bot';
  timestamp: Date;
}

const API_BASE_URL = envVariables.REACT_APP_API_URL;

export class ChatService {
  private static instance: ChatService;
  private controller: AbortController | null = null;
  private eventSource: EventSource | null = null;
  private sessionId: string | null = null;
  private pendingBackslash: string | null = null;

  public static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }

  generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substring(2);
  }

  public createUserMessage(content: string): ChatMessage {
    return {
      id: this.generateId(),
      message: content,
      role: 'user',
      timestamp: new Date(),
    };
  }

  public async getSesionMessages(id: string): Promise<[]> {
    const mensajes = <any>[];
    try {
      const url = `${API_BASE_URL}/conversacion/${id}`;
      const response = await customFetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const mensajes = await response.json();
      if (!mensajes) {
        throw new Error(`No se han encontrado sesiones`);
      }
    } catch (e) {
      throw new Error(`Error obteniendo sesiones`);
    }

    return mensajes;
  }

  public async sendMessage(
    mensajes: ChatMessage[],
    onChunk: (chunk: string) => void,
    onDone: () => void,
    onError: (error: Error) => void,
    datosIniciales: string,
  ): Promise<void> {
    this.cancelRequest();
    this.controller = new AbortController();

    const url = `${API_BASE_URL}/chat`;

    const mensajesToSend = (() => {
      const idx = mensajes.findIndex(m => m.role === 'user');
      if (idx === -1 || !datosIniciales) {
        return mensajes;
      }

      const updatedMessage: ChatMessage = {
        ...mensajes[idx],
        message: mensajes[idx].message + datosIniciales,
      };

      const copy = [...mensajes];
      copy[idx] = updatedMessage;
      return copy;
    })();

    const body: { mensaje: typeof mensajesToSend; idSesion?: string } = {
      mensaje: mensajesToSend,
      ...(this.sessionId ? { idSesion: this.sessionId } : {}),
    };

    try {
      const response = await customFetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify(body),
        signal: this.controller.signal,
      });

      if (!response.ok) {
        if (response.status == 401) {
          throw new Error(`Token expirado`, { cause: response.status });
        }
        throw new Error(`Error HTTP: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');

      if (!reader) {
        throw new Error('No se pudo leer el cuerpo de la respuesta');
      }

      await this.processStream(reader, decoder, onChunk, onDone);
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return;
      }
      onError(error as Error);
    } finally {
      this.closeConnection();
    }
  }

  async processStream(
    reader: ReadableStreamDefaultReader<Uint8Array>,
    decoder: TextDecoder,
    onChunk: (chunk: string) => void,
    onDone: () => void,
  ): Promise<void> {
    let done = false;

    while (!done) {
      const { value, done: readerDone } = await reader.read();
      done = readerDone;

      if (value) {
        const chunk = decoder.decode(value, { stream: true });
        const lines = this.extractValidLines(chunk);

        for (const line of lines) {
          this.processLine(line, onChunk, onDone);
        }
      }
    }
  }

  extractValidLines(chunk: string): string[] {
    return chunk
      .split('\n\n')
      .map(line => line.trim())
      .filter(line => line.startsWith('data: '));
  }

  processLine(line: string, onChunk: (chunk: string) => void, onDone: () => void): void {
    const jsonData = line.replace('data: ', '');
    const data = JSON.parse(jsonData);

    if (data.done === '[DONE]') {
      onDone();
    }

    if (data.chunk) {
      this.processChunk(data.chunk.replace(/\\n/g, '\n'), onChunk);
    }
  }

  processChunk(chunk: string, onChunk: (chunk: string) => void): void {
    // Caso especial: chunk es exactamente "\"
    if (chunk.endsWith('\\')) {
      this.pendingBackslash = chunk;
      return; // no llamamos aún a onChunk
    } else {
      // Si había un backslash pendiente, concatenamos
      if (this.pendingBackslash) {
        chunk = this.pendingBackslash + chunk;
        chunk = chunk.replace(/\\n/g, '\n');
        this.pendingBackslash = null;
      }

      if (this.isContextEvent(chunk)) {
        const events = chunk.split('][');
        events.forEach(e => {
          const itemId = this.extractItemId(e);
          const contextEvent = this.handleContextEvent(e, itemId);
          if (contextEvent) {
            onChunk(`[CONTEXT_EVENT]${JSON.stringify(contextEvent)}`);
          }
        });
      } else if (this.isSessionEvent(chunk)) {
        this.sessionId = this.extractSessionId(chunk);
      } else {
        onChunk(chunk);
      }
    }
  }

  isContextEvent(chunk: string): boolean {
    return (
      chunk.startsWith('[ADD_CONTEXT') || chunk.startsWith('[REMOVE_CONTEXT') || chunk.startsWith('[UPDATE_CONTEXT')
    );
  }

  isSessionEvent(chunk: string): boolean {
    return chunk.startsWith('[ID_SESION=');
  }

  extractItemId(chunk: string): string {
    return chunk.replace('[', '').replace(']', '').split('=')[1];
  }

  extractSessionId(chunk: string): string | null {
    const match = chunk.match(/\[ID_SESION=([^\]]+)\]/);
    if (match) {
      return match[1];
    } else {
      return null;
    }
  }

  handleContextEvent(chunk: string, itemId: string): { type: 'add' | 'update' | 'remove'; itemId: string } | null {
    if (chunk.includes('ADD_CONTEXT')) {
      return { type: 'add', itemId };
    }
    if (chunk.includes('UPDATE_CONTEXT')) {
      return { type: 'update', itemId };
    }
    if (chunk.includes('REMOVE_CONTEXT')) {
      return { type: 'remove', itemId };
    }
    return null;
  }

  public cancelRequest(): void {
    if (this.controller) {
      this.controller.abort();
      this.controller = null;
    }
    this.closeConnection();
  }

  public reiniciarSesion(): void {
    this.sessionId = null;
  }

  closeConnection(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}

export default ChatService.getInstance();
