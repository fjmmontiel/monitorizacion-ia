import React from 'react';
import Markdown from 'markdown-to-jsx';

import { ChatMessage } from '../../services/ChatService';

import { MessageRow, MessageContentWrapper, Bubble, Timestamp } from './ChatMessage.styles';

interface ChatMessageProps {
  message: ChatMessage;
}

const ChatMessageComponent: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const formattedTime = new Date(message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <MessageRow $isUser={isUser}>
      <MessageContentWrapper $isUser={isUser}>
        {/* <AvatarWrapper $isUser={isUser}>
          <Avatar $isUser={isUser}></Avatar>
        </AvatarWrapper> */}
        <div>
          <Bubble $isUser={isUser}>
            {/* <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.message}</ReactMarkdown> */}
            <Markdown>{message.message}</Markdown>
          </Bubble>
          {message.message != '' && <Timestamp $isUser={isUser}>{formattedTime}</Timestamp>}
        </div>
      </MessageContentWrapper>
    </MessageRow>
  );
};

export default ChatMessageComponent;
