import styled, { css } from 'styled-components';

import { ReactComponent as UnideskIALogo } from '../../assets/logos/unidesk_ia.svg';

export const ChatInterfaceContainer = styled.div`
  display: flex;
  flex-direction: column;
  background: ${({ theme }) => theme.colors.background.static.secondary};
  overflow: hidden;
  height: 100%;
`;

export const MessagesContainer = styled.div<{ $isEmpty: boolean }>`
  ::-webkit-scrollbar-track {
    background: ${({ theme }) => theme.colors.background.static.secondary}; /* <--- color del track (fondo) */
    border-radius: 6px;
  }

  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
  max-width: 69rem;
  margin: 0 auto;
  height: 100%;
  width: 100%;

  /* Si está vacío usamos flexbox centrado; si no, comportamiento normal */
  ${({ $isEmpty }) =>
    $isEmpty &&
    css`
      display: flex;
      align-items: center;
      justify-content: center;
    `}
`;

export const MessageWrapper = styled.div<{ $role: string }>`
  /* Puedes personalizar estilos según el rol si lo necesitas */
  &.message {
    margin-bottom: 0.5rem;
  }
`;

/* Contenedor del estado vacío con columna centrada y separación */
export const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
  padding: 16px;
`;

/* Ajusta tamaño del SVG según necesites */
export const EmptyLogoStyled = styled(UnideskIALogo)`
  width: 56px;
  height: 56px;
  display: block;
`;

/* Textos */
export const EmptyTitle = styled.h3`
  margin: 0;
  color: ${({ theme }) => theme.colors.content.interactive.primary.default};
  ${({ theme }) =>
    theme.typography.generateFontStyle({
      size: 'l',
      weight: 'bold',
    })};
`;

export const EmptySubtitle = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.content.static.primary};
  ${({ theme }) =>
    theme.typography.generateFontStyle({
      size: 'm',
      weight: 'bold',
    })};
`;

/* Contenedor del estado vacío con columna centrada y separación */
export const ButtonContainer = styled.div`
  max-width: 69rem;
  margin: 0 auto;
  width: 100%;
  padding: 16px;
`;

export const FooterContainer = styled.div`
  padding: 16px;
`;

export const Disclaimer = styled.p`
  display: none;
  text-align: center;
  margin-top: 0;
  ${({ theme }) =>
    theme.typography.generateFontStyle({
      size: 'xs',
    })};
`;
