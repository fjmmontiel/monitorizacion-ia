import React, { useRef, useEffect, useCallback, useState } from 'react';
import { Button } from '@internal-channels-components/button';
import { Dialog } from '@internal-channels-components/dialog';

import ChatMessageComponent from '../ChatMessage/ChatMessage';
import ChatInput from '../ChatInput/ChatInput';
import chatService, { ChatMessage } from '../../services/ChatService';
import contextService from '../../services/ContextService';
import { useContextManager } from '../../hooks/useContextManager';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { useAppQueryParams } from '../../hooks/AppQueryParamsContext';

import {
  ChatInterfaceContainer,
  Disclaimer,
  EmptyLogoStyled,
  EmptyState,
  EmptySubtitle,
  EmptyTitle,
  FooterContainer,
  MessagesContainer,
  MessageWrapper,
} from './ChatInterface.styles';
import { msg_mock } from './mensajes_mock';

type ChatInterfaceProps = {
  idSesion?: string; // opcional
};

const ChatInterface: React.FC<ChatInterfaceProps> = ({ idSesion }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [dialogVisible, setDialogVisible] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const qp = useAppQueryParams();
  const { addItemToContext, deleteItemFromContext } = useContextManager();
  const { showToast } = useToast();
  const { refreshToken, startSSOAuth } = useAuth();

  const headerContent = <span>Atención</span>;

  const footerContent = (
    <FooterContainer>
      <Button label="No" onClick={() => setDialogVisible(false)} variant="secondary" />
      <Button label="Si" onClick={() => reiniciarConversacion()} />
    </FooterContainer>
  );

  useEffect(() => {
    if (idSesion) {
      // Obtener conversación
      getSesionMessages(idSesion);
    }

    return () => {
      chatService.cancelRequest();
    };
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  async function getSesionMessages(id: string) {
    setIsLoading(true);
    try {
      const msg = await chatService.getSesionMessages(id);
      setMessages(msg);
    } catch (e) {
      const msg = JSON.parse(msg_mock);
      setMessages(msg);
      // showToast({
      //   severity: 'error',
      //   life: 3000,
      //   detail: `id sesión: ${id}`,
      //   summary: 'Error recuperando conversación',
      //   sticky: false,
      // });
    } finally {
      setIsLoading(false);
    }
  }

  const sendMessage = useCallback(
    async (inputMessage: string) => {
      if (!inputMessage.trim() || isLoading) return;

      const claperGestor = qp.get('claperGestor');
      const centro = qp.get('centro');
      const claperUsuario = qp.get('claperUsuario');
      const nifUsuario = qp.get('nifUsuario');

      const datosIniciales = `
        ${claperGestor ? `- CODIGO_GESTOR: ${claperGestor}` : ''}
        ${centro ? `- CENTRO: ${centro}` : ''}
        ${claperUsuario ? `- CLAPER_USUARIO: ${claperUsuario}` : ''}
        ${nifUsuario ? `- NIF_USUARIO: ${nifUsuario}` : ''}
        **${
          nifUsuario
            ? `SE ESTÁ ACCEDIENDO DESDE LA FICHA DE CLIENTE`
            : `SE ESTÁ ACCEDIENDO DESDE LA OPERATIVA DE NO CLIENTES`
        }**`;

      const userMessage = chatService.createUserMessage(inputMessage);
      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);

      const assistantMessage: ChatMessage = {
        id: 'bot-' + Date.now(),
        message: '',
        role: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      try {
        const currentMessages = [...messages, userMessage];

        await chatService.sendMessage(
          currentMessages,
          chunk => {
            if (chunk.startsWith('[CONTEXT_EVENT]')) {
              const event = JSON.parse(chunk.replace('[CONTEXT_EVENT]', ''));
              if (event.type === 'add' || event.type === 'update') {
                addItemToContext(event.itemId);
              } else if (event.type === 'remove') {
                deleteItemFromContext(event.itemId);
              }
            } else {
              setMessages(prev =>
                prev.map(msg => (msg.id === assistantMessage.id ? { ...msg, message: msg.message + chunk } : msg)),
              );
            }
          },
          () => setIsLoading(false),
          errorHandler,
          datosIniciales,
        );
      } catch {
        setIsLoading(false);
      }
    },
    [isLoading, messages, qp, addItemToContext, deleteItemFromContext],
  );

  function errorHandler(error: Error) {
    setIsLoading(false);
    if (error.cause === 400) {
      startSSOAuth();
    } else if (error.cause === 401) {
      refreshToken('sso');
      showToast({
        severity: 'error',
        detail: `La sesión ha expirado y se ha reiniciado. Cierre este mensaje y vuelva a envia el mensaje.`,
        summary: 'Error',
        sticky: true,
      });
    } else {
      showToast({
        severity: 'error',
        detail: `Se ha producido un error inesperado. Inténtalo de nuevo.`,
        summary: 'Error',
        sticky: true,
      });
    }
  }

  function reiniciarConversacion(): void {
    setDialogVisible(false);
    setMessages([]);
    chatService.reiniciarSesion();
    contextService.reiniciarContexto();
  }

  const isEmpty = messages.length === 0;

  return (
    <ChatInterfaceContainer id="chat-interface">
      {/* {!isEmpty && (
        <ButtonContainer>
          <Button
            disabled={isLoading}
            label="Nueva conversación"
            icon={<Icon name="mailChatManual" width={20} height={20} color="white"></Icon>}
            onClick={() => {
              setDialogVisible(true);
            }}></Button>
        </ButtonContainer>
      )} */}
      <Dialog
        visible={dialogVisible}
        modal
        header={headerContent}
        footer={footerContent}
        style={{ width: '32rem' }}
        onHide={() => {
          if (!dialogVisible) return;
          setDialogVisible(false);
        }}>
        <p>
          Se va a proceder a eliminar historial de la conversación así como los datos almacenados en el contexto. ¿Desea
          continuar?
        </p>
      </Dialog>

      <MessagesContainer $isEmpty={isEmpty}>
        {isEmpty ? (
          <EmptyState>
            <EmptyLogoStyled />
            <EmptyTitle>Bienvenido/a</EmptyTitle>
            <EmptySubtitle>
              Soy un asistente de Inteligencia Artificial. Genero todas mis respuestas a partir de la información
              corporativa y es necesario que las revises antes de tomar decisiones.
            </EmptySubtitle>
          </EmptyState>
        ) : (
          <>
            {messages.map(message => (
              <MessageWrapper key={message.id} $role={message.role}>
                <ChatMessageComponent message={message} />
              </MessageWrapper>
            ))}
          </>
        )}
        <div ref={messagesEndRef} />
      </MessagesContainer>
      {typeof idSesion !== 'string' && (
        <>
          <ChatInput onSendMessage={sendMessage} disabled={isLoading} />
          <Disclaimer>
            Esta herramienta proporciona información de precios con el nivel de riesgo más bajo para no clientes, con
            independencia de si se ha iniciado desde la visión 360 de un cliente.
          </Disclaimer>
        </>
      )}
    </ChatInterfaceContainer>
  );
};

export default ChatInterface;
