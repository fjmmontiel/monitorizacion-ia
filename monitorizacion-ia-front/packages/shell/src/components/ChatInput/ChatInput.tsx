import React from 'react';
import { Icon } from '@internal-channels-components/icon';
import { IconButton } from '@internal-channels-components/icon-button';
import { ProgressSpinner } from '@internal-channels-components/progress-spinner';

import {
  ButtonRecordStyles,
  ButtonSendStyles,
  Container,
  InputContainer,
  LoadingStyles,
  StyledTextArea,
} from './ChatInput.styles';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = React.useState('');
  const [isRecording, setIsRecording] = React.useState(false);
  const [speechSupported, setSpeechSupported] = React.useState<boolean>(false);
  const recognitionRef = React.useRef<any | null>(null);
  const mediaStreamRef = React.useRef<MediaStream | null>(null);
  const warmedUpRef = React.useRef(false);
  const textareaRef = React.useRef<HTMLTextAreaElement | null>(null);
  const finalTranscriptRef = React.useRef<string>(''); // acumula solo textos finales
  const messageRef = React.useRef(message);

  React.useEffect(() => {
    messageRef.current = message;
  }, [message]);

  React.useEffect(() => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition || null;
    setSpeechSupported(Boolean(SpeechRecognition));

    if (!SpeechRecognition) return;

    try {
      const recog = new SpeechRecognition();
      recog.lang = 'es-ES';
      recog.interimResults = false;
      recog.maxAlternatives = 1;

      recog.onstart = () => {
        finalTranscriptRef.current = messageRef.current || '';
        setIsRecording(true);
      };

      recog.onresult = (event: any) => {
        // Con interimResults = false solo llegan resultados finales aquí.
        let appended = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          const transcript = result[0]?.transcript ?? '';
          if (transcript) appended += ' ' + transcript;
        }
        if (appended) {
          finalTranscriptRef.current = (finalTranscriptRef.current + appended).trim();
          setMessage(finalTranscriptRef.current);
        }
      };

      // recog.onerror = (e: any) => {
      //   //console.error('SpeechRecognition error', e);
      // };

      recog.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recog;
    } catch (err) {
      //console.error('Error inicializando SpeechRecognition', err);
      recognitionRef.current = null;
    }

    return () => {
      try {
        recognitionRef.current?.stop?.();
      } catch {
        mediaStreamRef.current = null;
      }
      recognitionRef.current = null;
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(t => t.stop());
        mediaStreamRef.current = null;
      }
    };
  }, []);

  // Solicita micrófono y mantiene stream hasta stopRecognition
  const warmUpMicrophone = async () => {
    if (warmedUpRef.current) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      warmedUpRef.current = true;
    } catch (err) {
      //console.warn('No permission or error opening mic', err);
      warmedUpRef.current = false;
    }
  };

  // Enfocar el textarea cuando la prop disabled cambie a true
  React.useEffect(() => {
    if (!disabled) {
      textareaRef.current?.focus();
    }
  }, [disabled]);

  const handleSendMessage = () => {
    if (message.trim() && !disabled && !isRecording) {
      onSendMessage(message.trim());
      setMessage('');
      finalTranscriptRef.current = '';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startRecognition = async () => {
    if (disabled || isRecording) return;
    const recog = recognitionRef.current;
    if (!recog) {
      setSpeechSupported(false);
      return;
    }

    // Si no está warmed-up, intenta calentar (esto suele resolverse rápido si ya hubo pointerdown)
    if (!warmedUpRef.current) {
      await warmUpMicrophone();
    }

    try {
      // Limpia mensaje interino si prefieres empezar desde vacío
      // setMessage('');
      recog.start();
    } catch (err) {
      //console.error('Error iniciando reconocimiento', err);
      setIsRecording(false);
    }
  };

  const stopRecognition = () => {
    const recog = recognitionRef.current;
    if (!recog) {
      setIsRecording(false);
      return;
    }
    try {
      recog.stop();
    } catch (err) {
      //console.error('Error deteniendo SpeechRecognition', err);
    } finally {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(t => t.stop());
        mediaStreamRef.current = null;
      }
      warmedUpRef.current = false;
    }
  };

  const handleRecordClick = () => {
    if (disabled) return;
    if (!isRecording) {
      startRecognition();
    } else {
      stopRecognition();
    }
  };

  // En la presión corta del botón (pointerdown) hacemos warmUp para que la petición de permiso no
  // se solape con start en el click posterior; no bloqueamos la UX porque es rápido.
  const handleRecordPointerDown = async () => {
    if (disabled || isRecording) return;
    // kick off permission prompt early (user gesture)
    warmUpMicrophone();
  };

  return (
    <Container>
      <InputContainer data-testid="message-input-container">
        <StyledTextArea
          ref={textareaRef}
          data-testid="message-textarea"
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Introduce tu consulta..."
          disabled={disabled || isRecording}
          readOnly={disabled || isRecording}
          aria-disabled={disabled || isRecording}
        />
        {!disabled ? (
          <ButtonSendStyles data-testid="send-button-container">
            <IconButton
              icon={<Icon name="mailSendEmail" width={20} height={20} color="white" />}
              aria-label="Enviar comentario"
              onClick={handleSendMessage}
              disabled={!message.trim() || disabled || isRecording}
              data-testid="send-button"
            />
          </ButtonSendStyles>
        ) : (
          <LoadingStyles data-testid="loading">
            <ProgressSpinner strokeWidth="4" />
          </LoadingStyles>
        )}

        {speechSupported && (
          <ButtonRecordStyles
            aria-label={isRecording ? 'Detener grabación' : 'Grabar comentario'}
            onPointerDown={handleRecordPointerDown}
            onClick={handleRecordClick}
            onContextMenu={e => e.preventDefault()}
            disabled={disabled}
            data-testid={isRecording ? 'stop-record-button' : 'record-button'}>
            <Icon name={isRecording ? 'controlButtonStop' : 'computerVoiceMail'} width={20} height={20} />
          </ButtonRecordStyles>
        )}
      </InputContainer>
    </Container>
  );
};

export default ChatInput;
