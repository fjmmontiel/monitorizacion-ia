/* eslint-disable testing-library/no-node-access */
import '@testing-library/jest-dom';
import { global } from '@internal-channels-components/theme';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import { AppThemeProvider } from '#/shell/theme';

import ChatInput from '../../../src/components/ChatInput/ChatInput';

jest.mock('@internal-channels-components/textarea', () => ({
  Textarea: ({ value, placeholder, onChange, onKeyDown, label, 'data-testid': testId }: any) => (
    <div>
      <label>{label}</label>
      <textarea
        data-testid={testId || 'textarea'}
        value={value}
        onChange={onChange}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
      />
    </div>
  ),
}));

jest.mock('@internal-channels-components/button', () => ({
  Button: ({ label, onClick, disabled, 'data-testid': testId }: any) => (
    <button data-testid={testId || 'button'} onClick={onClick} disabled={disabled}>
      {label}
    </button>
  ),
}));

jest.mock('@internal-channels-components/progress-spinner', () => ({
  ProgressSpinner: () => <div></div>,
}));

jest.mock('@internal-channels-components/icon-button', () => ({
  IconButton: ({ label, onClick, disabled, 'data-testid': testId }: any) => (
    <button data-testid={testId || 'button'} onClick={onClick} disabled={disabled}>
      {label}
    </button>
  ),
}));

describe('ChatInput', () => {
  it('renders textarea and send button', () => {
    render(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={jest.fn()} />
      </AppThemeProvider>,
    );
    expect(screen.getByPlaceholderText(/Introduce tu consulta.../i)).toBeInTheDocument();
    expect(screen.getByTestId('send-button')).toBeInTheDocument();
  });

  it('calls onSendMessage when send button is clicked with non-empty message', () => {
    const onSendMessage = jest.fn();
    render(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={onSendMessage} />
      </AppThemeProvider>,
    );
    const textarea = screen.getByPlaceholderText(/Introduce tu consulta.../i);
    const button = screen.getByTestId('send-button');

    fireEvent.change(textarea, { target: { value: 'Hello' } });
    fireEvent.click(button);

    expect(onSendMessage).toHaveBeenCalledWith('Hello');
    expect(textarea).toHaveValue('');
  });

  it('does not call onSendMessage when send button is clicked with empty message', () => {
    const onSendMessage = jest.fn();

    render(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={onSendMessage} />
      </AppThemeProvider>,
    );
    const button = screen.getByTestId('send-button');
    fireEvent.click(button);
    expect(onSendMessage).not.toHaveBeenCalled();
  });

  it('calls onSendMessage and clears textarea on Enter key (not Shift+Enter)', () => {
    const onSendMessage = jest.fn();
    render(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={onSendMessage} />
      </AppThemeProvider>,
    );
    const textarea = screen.getByPlaceholderText(/Introduce tu consulta.../i);

    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });

    expect(onSendMessage).toHaveBeenCalledWith('Test message');
    expect(textarea).toHaveValue('');
  });

  it('does not send message on Shift+Enter', () => {
    const onSendMessage = jest.fn();
    render(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={onSendMessage} />
      </AppThemeProvider>,
    );
    const textarea = screen.getByPlaceholderText(/Introduce tu consulta.../i);

    fireEvent.change(textarea, { target: { value: 'Line 1' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });

    expect(onSendMessage).not.toHaveBeenCalled();
    expect(textarea).toHaveValue('Line 1');
  });

  it('show loading when disabled', () => {
    const { rerender } = render(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={jest.fn()} />
      </AppThemeProvider>,
    );
    const button = screen.getByTestId('send-button');
    expect(button).toBeDisabled();

    const textarea = screen.getByPlaceholderText(/Introduce tu consulta.../i);
    fireEvent.change(textarea, { target: { value: 'abc' } });
    expect(button).toBeEnabled();

    rerender(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={jest.fn()} disabled />
      </AppThemeProvider>,
    );
    const loading = screen.getByTestId('loading');
    expect(loading).toBeVisible();
  });
});

describe('ChatInput - speech and microphone behaviour', () => {
  const originalSpeech = (window as any).SpeechRecognition;
  const originalWebkit = (window as any).webkitSpeechRecognition;
  const originalGetUserMedia = navigator.mediaDevices?.getUserMedia;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    (window as any).SpeechRecognition = originalSpeech;
    (window as any).webkitSpeechRecognition = originalWebkit;
    if (navigator.mediaDevices) {
      // @ts-ignore
      navigator.mediaDevices.getUserMedia = originalGetUserMedia;
    }
  });

  it('disables record button when SpeechRecognition is not available', () => {
    (window as any).SpeechRecognition = undefined;
    (window as any).webkitSpeechRecognition = undefined;

    render(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={jest.fn()} />
      </AppThemeProvider>,
    );

    const recordBtn = screen.queryByTestId('record-button');
    expect(recordBtn).not.toBeInTheDocument();
  });

  it('calls getUserMedia on pointerdown (warm up) and enables recording start', async () => {
    // Mock SpeechRecognition ctor
    const mockStart = jest.fn();
    const mockStop = jest.fn();
    class MockRecog {
      lang = '';
      interimResults = false;
      maxAlternatives = 1;
      onstart: any = null;
      onresult: any = null;
      onend: any = null;
      onerror: any = null;
      start() {
        mockStart();
        if (this.onstart) {
          this.onstart();
        }
      }
      stop() {
        mockStop();
        if (this.onend) {
          this.onend();
        }
      }
    }
    (window as any).SpeechRecognition = MockRecog;

    // Mock getUserMedia
    const mockTrack = { stop: jest.fn() };
    const mockStream = { getTracks: () => [mockTrack] } as any;
    // @ts-ignore
    navigator.mediaDevices = { getUserMedia: jest.fn().mockResolvedValue(mockStream) };

    render(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={jest.fn()} />
      </AppThemeProvider>,
    );

    const recordBtn = screen.getByTestId('record-button');

    // pointerdown should warm up mic (getUserMedia called)
    fireEvent.pointerDown(recordBtn);
    // waitFor will retry until the mock was called
    await waitFor(() => {
      // @ts-ignore
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({ audio: true });
    });

    // click should start recognition (and change testid to stop-record-button by isRecording state)
    fireEvent.click(recordBtn);

    // After start, UI shows stop button (isRecording true)
    await waitFor(() => {
      expect(screen.getByTestId('stop-record-button')).toBeInTheDocument();
    });

    // click stop should stop recognition and stop tracks
    const stopBtn = screen.getByTestId('stop-record-button');
    fireEvent.click(stopBtn);

    // wait until the mock track stop has been called
    await waitFor(() => {
      expect(mockTrack.stop).toHaveBeenCalled();
    });
  });

  it('accumulates final transcript and sets textarea value on onresult final', async () => {
    let recogInstance: any = null;
    class MockRecog {
      lang = '';
      interimResults = false;
      maxAlternatives = 1;
      onstart: any = null;
      onresult: any = null;
      onend: any = null;
      onerror: any = null;
      start() {
        if (this.onstart) {
          this.onstart();
        }
      }
      stop() {
        if (this.onend) {
          this.onend();
        }
      }
    }
    (window as any).SpeechRecognition = MockRecog;

    // @ts-ignore
    navigator.mediaDevices = { getUserMedia: jest.fn().mockResolvedValue({ getTracks: () => [] }) };

    // Spy on constructor to capture instance
    const ctorSpy = jest.spyOn(window as any, 'SpeechRecognition').mockImplementation(function (this: any) {
      recogInstance = new MockRecog();
      return recogInstance;
    });

    render(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={jest.fn()} />
      </AppThemeProvider>,
    );

    const recordBtn = screen.getByTestId('record-button');

    // start recording (pointerDown warms up, click starts)
    fireEvent.pointerDown(recordBtn);
    await waitFor(() => {
      // @ts-ignore
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalled();
    });
    fireEvent.click(recordBtn);

    // wait until UI shows that recording started
    await waitFor(() => {
      expect(screen.getByTestId('stop-record-button')).toBeInTheDocument();
    });

    // Simulate onresult with final results (SpeechRecognitionEvent-like)
    const fakeEvent = {
      resultIndex: 0,
      results: [
        {
          0: { transcript: 'hola' },
          isFinal: true,
        },
      ],
    };

    // Call handler directly and wait for DOM update
    recogInstance.onresult(fakeEvent);
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Introduce tu consulta.../i)).toHaveValue('hola');
    });

    // Simulate another final chunk and expect accumulation
    const fakeEvent2 = {
      resultIndex: 0,
      results: [
        {
          0: { transcript: '¿cómo estás?' },
          isFinal: true,
        },
      ],
    };

    recogInstance.onresult(fakeEvent2);
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Introduce tu consulta.../i)).toHaveValue('hola ¿cómo estás?');
    });

    ctorSpy.mockRestore();
  });

  it('focuses textarea when disabled prop toggles from true to false', () => {
    const { rerender } = render(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={jest.fn()} disabled />
      </AppThemeProvider>,
    );

    const textarea = screen.getByPlaceholderText(/Introduce tu consulta.../i) as HTMLTextAreaElement;

    // Initially disabled, not focused
    expect(textarea).not.toHaveFocus();

    // Rerender with disabled = false and expect focus
    rerender(
      <AppThemeProvider theme={global}>
        <ChatInput onSendMessage={jest.fn()} disabled={false} />
      </AppThemeProvider>,
    );

    expect(textarea).toHaveFocus();
  });
});
