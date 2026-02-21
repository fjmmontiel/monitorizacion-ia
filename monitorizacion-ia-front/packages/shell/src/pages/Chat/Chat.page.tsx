/* istanbul ignore file */
import { useState } from 'react';

import ChatInterface from '#/shell/components/ChatInterface/ChatInterface';
import ContextPanel from '#/shell/components/ContextPanel/ContextPanel';

import { Main, LeftPanel, Divider, RightPanel } from './Chat.styles';

type ChatPageProps = {
  idSesion?: string; // opcional
};

// eslint-disable-next-line react/prop-types
const ChatPage: React.FC<ChatPageProps> = ({ idSesion }) => {
  const [leftWidth, setLeftWidth] = useState(70);

  const handleMouseDown = (e: React.MouseEvent) => {
    const startX = e.clientX;
    const startWidth = leftWidth;

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const deltaX = moveEvent.clientX - startX;
      const newWidth = Math.min(80, Math.max(20, startWidth + (deltaX / window.innerWidth) * 100));
      setLeftWidth(newWidth);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <Main $isSesionDetail={typeof idSesion == 'string'}>
      <LeftPanel style={{ width: `${leftWidth}%` }}>
        <ChatInterface idSesion={idSesion} />
      </LeftPanel>
      <Divider onMouseDown={handleMouseDown} />
      <RightPanel style={{ width: `${100 - leftWidth}%` }}>
        <ContextPanel idSesion={idSesion} />
      </RightPanel>
    </Main>
  );
};

export default ChatPage;
