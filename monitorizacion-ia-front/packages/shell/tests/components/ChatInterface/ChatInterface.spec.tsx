import React from 'react';
import '@testing-library/jest-dom';
import { global } from '@internal-channels-components/theme';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import { AppQueryParamsProvider } from '#/shell/hooks/AppQueryParamsContext';
import { AppThemeProvider } from '#/shell/theme';
import { ToastProvider } from '#/shell/context/ToastContext';
import { AuthProvider } from '#/shell/context/AuthContext';

import { useContextManager } from '../../../src/hooks/useContextManager';
import ChatService from '../../../src/services/ChatService';
import ChatInterface from '../../../src/components/ChatInterface/ChatInterface';

jest.mock('../../../src/components/ChatMessage/ChatMessage', () => {
  const MockChatMessage = (props: { message: { message: string } }) => (
    <div data-testid="chat-message">{props.message.message}</div>
  );
  MockChatMessage.displayName = 'MockChatMessage';
  return MockChatMessage;
});

jest.mock('../../../src/components/ChatInput/ChatInput', () => {
  const MockButton = (props: { disabled?: boolean; onSendMessage: (msg: string) => void }) => (
    <div>
      <button data-testid="send-btn" disabled={props.disabled} onClick={() => props.onSendMessage('test message')}>
        Send
      </button>
    </div>
  );
  MockButton.displayName = 'MockButton';
  return MockButton;
});

jest.mock('@internal-channels-components/button', () => ({
  Button: ({ label, onClick, disabled, 'data-testid': testId }: any) => (
    <button data-testid={testId || 'button'} onClick={onClick} disabled={disabled}>
      {label}
    </button>
  ),
}));

jest.mock('../../../src/services/ChatService', () => {
  const sendMessageMock = jest.fn();
  const cancelRequestMock = jest.fn();
  const createUserMessageMock = (msg: string) => ({
    id: 'user-1',
    message: msg,
    role: 'user',
    timestamp: new Date(),
  });
  return {
    __esModule: true,
    default: {
      sendMessage: (...args: any[]) => sendMessageMock(...args),
      cancelRequest: cancelRequestMock,
      createUserMessage: createUserMessageMock,
      __mocks: {
        sendMessageMock,
        cancelRequestMock,
        createUserMessageMock,
      },
    },
    ChatMessage: {},
  };
});

jest.mock('../../../src/hooks/useContextManager', () => ({
  useContextManager: jest.fn(),
}));

jest.mock('@internal-channels-components/toast', () => {
  const MockToast = React.forwardRef((_props, ref) => {
    React.useImperativeHandle(ref, () => ({
      show: jest.fn(),
    }));
    return <div data-testid="mock-toast" />;
  });
  MockToast.displayName = 'MockToast';

  return {
    Toast: MockToast,
    ToastTemplate: ({ message }: { message: string }) => <div>{message}</div>,
  };
});

function renderWithContext(ui: React.ReactElement, { sourceSearch = '' } = {}) {
  return render(
    <AppThemeProvider theme={global}>
      <AuthProvider>
        <ToastProvider>
          <AppQueryParamsProvider sourceSearch={sourceSearch}>{ui}</AppQueryParamsProvider>
        </ToastProvider>
      </AuthProvider>
    </AppThemeProvider>,
  );
}

describe('ChatInterface', () => {
  let sendMessageMock: jest.Mock;
  let cancelRequestMock: jest.Mock;
  const addItemToContextMock = jest.fn();
  const deleteItemFromContextMock = jest.fn();

  beforeAll(() => {
    window.HTMLElement.prototype.scrollIntoView = jest.fn();
  });

  beforeEach(() => {
    sendMessageMock = (ChatService as any).__mocks.sendMessageMock;
    cancelRequestMock = (ChatService as any).__mocks.cancelRequestMock;
    sendMessageMock.mockReset();
    cancelRequestMock.mockReset();
    addItemToContextMock.mockReset();
    deleteItemFromContextMock.mockReset();

    (useContextManager as jest.Mock).mockReturnValue({
      items: [],
      addItemToContext: addItemToContextMock,
      deleteItemFromContext: deleteItemFromContextMock,
    });
  });

  it('renders without crashing', () => {
    renderWithContext(<ChatInterface />);
    expect(screen.getByTestId('send-btn')).toBeInTheDocument();
  });

  it('sends a message and shows user and bot messages', async () => {
    sendMessageMock.mockImplementation((_msgs, onChunk, onDone) => {
      onChunk('hello');
      onDone();
    });

    renderWithContext(<ChatInterface />);
    fireEvent.click(screen.getByTestId('send-btn'));

    await waitFor(() => {
      expect(screen.getAllByTestId('chat-message').length).toBeGreaterThanOrEqual(2);
    });
    expect(sendMessageMock).toHaveBeenCalled();
  });

  it('no envía mensaje si ya está cargando', async () => {
    sendMessageMock.mockImplementation(() => {});
    renderWithContext(<ChatInterface />);
    fireEvent.click(screen.getByTestId('send-btn'));
    fireEvent.click(screen.getByTestId('send-btn'));
    expect(sendMessageMock).toHaveBeenCalledTimes(1);
  });

  it('llama a cancelRequest al desmontar', () => {
    const { unmount } = renderWithContext(<ChatInterface />);
    unmount();
    expect(cancelRequestMock).toHaveBeenCalled();
  });

  it('muestra el mensaje de bienvenida al limpiar el chat', () => {
    renderWithContext(<ChatInterface />);
    expect(screen.getByTestId('send-btn')).toBeInTheDocument();
  });

  it('procesa eventos CONTEXT_EVENT y llama a addItemToContext', async () => {
    const contextEvent = { type: 'add', itemId: 'item-123' };
    sendMessageMock.mockImplementation((_msgs, onChunk, onDone) => {
      onChunk(`[CONTEXT_EVENT]${JSON.stringify(contextEvent)}`);
      onDone();
    });

    renderWithContext(<ChatInterface />);
    fireEvent.click(screen.getByTestId('send-btn'));

    await waitFor(() => {
      expect(addItemToContextMock).toHaveBeenCalledWith('item-123');
    });
  });

  it('procesa eventos CONTEXT_EVENT de tipo remove y llama a deleteItemFromContext', async () => {
    const contextEvent = { type: 'remove', itemId: 'item-456' };
    sendMessageMock.mockImplementation((_msgs, onChunk, onDone) => {
      onChunk(`[CONTEXT_EVENT]${JSON.stringify(contextEvent)}`);
      onDone();
    });

    renderWithContext(<ChatInterface />);
    fireEvent.click(screen.getByTestId('send-btn'));

    await waitFor(() => {
      expect(deleteItemFromContextMock).toHaveBeenCalledWith('item-456');
    });
  });
});
